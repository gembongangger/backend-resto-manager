from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from ..extensions import db
from ..models import MenuItem, MenuCategory, Recipe
from ..services.auth import require_roles, get_restaurant_id
from ..services.upload import upload_image

bp = Blueprint("menu", __name__)


@bp.get("")
@jwt_required()
def list_menu():
    include_inactive = request.args.get("include_inactive") == "1"
    restaurant_id = get_restaurant_id()
    query = MenuItem.query.filter_by(restaurant_id=restaurant_id)
    if not include_inactive:
        query = query.filter_by(is_active=True)
    items = query.order_by(MenuItem.id.asc()).all()
    return jsonify([
        {
            "id": item.id,
            "name": item.name,
            "category_id": item.category_id,
            "category_name": item.category.name if item.category else None,
            "price": item.price,
            "profit": item.profit,
            "image_url": item.image_url,
            "is_active": item.is_active,
        }
        for item in items
    ])


@bp.post("")
@jwt_required()
@require_roles("admin")
def create_menu_item():
    is_json = request.is_json
    
    if is_json:
        data = request.get_json(silent=True) or {}
        name = data.get("name")
        price = data.get("price")
        category_id = data.get("category_id")
        profit = data.get("profit", 0)
        image_url = data.get("image_url")
    else:
        name = request.form.get("name")
        price = request.form.get("price")
        category_id = request.form.get("category_id")
        profit = request.form.get("profit", "0")
        
        image_url = request.form.get("image_url")
        
        try:
            if request.files:
                image_file = request.files.get("image")
                if image_file:
                    image_url = upload_image(image_file)
        except Exception:
            pass

    if not name or price is None:
        return jsonify({"error": "name_and_price_required"}), 400

    restaurant_id = get_restaurant_id()
    if category_id is not None:
        category_id = int(category_id)
        category = MenuCategory.query.filter_by(id=category_id, restaurant_id=restaurant_id).first()
        if not category:
            return jsonify({"error": "category_not_found"}), 404

    item = MenuItem(
        name=name,
        category_id=category_id,
        price=int(price),
        profit=int(profit or 0),
        image_url=image_url,
        restaurant_id=restaurant_id
    )
    db.session.add(item)
    db.session.commit()

    return jsonify({
        "id": item.id,
        "name": item.name,
        "category_id": item.category_id,
        "category_name": item.category.name if item.category else None,
        "price": item.price,
        "profit": item.profit,
        "image_url": item.image_url
    }), 201


@bp.put("/<int:item_id>")
@jwt_required()
@require_roles("admin")
def update_menu_item(item_id: int):
    is_json = request.is_json
    data = request.get_json(silent=True) if is_json else {}
    restaurant_id = get_restaurant_id()
    item = MenuItem.query.filter_by(id=item_id, restaurant_id=restaurant_id).first()
    if not item:
        return jsonify({"error": "not_found"}), 404

    name = request.form.get("name") if not is_json else data.get("name")
    if name is not None:
        item.name = name

    category_id = request.form.get("category_id") if not is_json else data.get("category_id")
    if category_id is not None:
        if category_id == "" or category_id is None:
            item.category_id = None
        else:
            category_id_int = int(category_id)
            category = MenuCategory.query.filter_by(id=category_id_int, restaurant_id=restaurant_id).first()
            if not category:
                return jsonify({"error": "category_not_found"}), 404
            item.category_id = category_id_int

    price = request.form.get("price") if not is_json else data.get("price")
    if price is not None:
        item.price = int(price)

    profit = request.form.get("profit") if not is_json else data.get("profit")
    if profit is not None:
        item.profit = int(profit)
    
    image_url = None
    if is_json:
        image_url = data.get("image_url")
    else:
        image_file = None
        try:
            if request.files:
                image_file = request.files.get("image")
        except Exception:
            pass
        if image_file:
            image_url = upload_image(image_file)
        else:
            image_url = request.form.get("image_url")
    
    if image_url is not None:
        item.image_url = image_url

    is_active = request.form.get("is_active") if not is_json else data.get("is_active")
    if is_active is not None:
        item.is_active = bool(is_active)

    db.session.commit()

    return jsonify({
        "id": item.id,
        "name": item.name,
        "category_id": item.category_id,
        "category_name": item.category.name if item.category else None,
        "price": item.price,
        "profit": item.profit,
        "image_url": item.image_url,
        "is_active": item.is_active
    })


@bp.delete("/<int:item_id>")
@jwt_required()
@require_roles("admin")
def delete_menu_item(item_id: int):
    restaurant_id = get_restaurant_id()
    item = MenuItem.query.filter_by(id=item_id, restaurant_id=restaurant_id).first()
    if not item:
        return jsonify({"error": "not_found"}), 404

    Recipe.query.filter_by(menu_item_id=item_id).delete()
    db.session.delete(item)
    db.session.commit()

    return jsonify({"status": "deleted"})
