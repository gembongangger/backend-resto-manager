from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

from ..extensions import db
from ..models import Recipe, MenuItem, KitchenInventory, Restaurant
from ..services.auth import require_roles, get_restaurant_id

bp = Blueprint("recipes", __name__)


@bp.get("/menu/<int:menu_item_id>")
@jwt_required()
def get_recipes(menu_item_id: int):
    restaurant_id = get_restaurant_id()
    recipes = Recipe.query.filter_by(menu_item_id=menu_item_id, restaurant_id=restaurant_id).all()
    return jsonify([
        {
            "id": r.id,
            "menu_item_id": r.menu_item_id,
            "inventory_item_id": r.inventory_item_id,
            "inventory_name": r.inventory_item.name,
            "inventory_unit": r.inventory_item.unit,
            "quantity": r.quantity,
        }
        for r in recipes
    ])


@bp.post("")
@jwt_required()
@require_roles("admin")
def create_recipe():
    data = request.get_json(silent=True) or {}
    menu_item_id = data.get("menu_item_id")
    inventory_item_id = data.get("inventory_item_id")
    quantity = data.get("quantity", 1)

    if not menu_item_id or not inventory_item_id:
        return jsonify({"error": "menu_item_id_and_inventory_item_id_required"}), 400

    restaurant_id = get_restaurant_id()
    
    menu_item = MenuItem.query.filter_by(id=menu_item_id, restaurant_id=restaurant_id).first()
    if not menu_item:
        return jsonify({"error": "menu_item_not_found"}), 404
    
    inventory_item = KitchenInventory.query.filter_by(id=inventory_item_id, restaurant_id=restaurant_id).first()
    if not inventory_item:
        return jsonify({"error": "inventory_item_not_found"}), 404

    existing = Recipe.query.filter_by(menu_item_id=menu_item_id, inventory_item_id=inventory_item_id, restaurant_id=restaurant_id).first()
    if existing:
        existing.quantity = quantity
        db.session.commit()
        return jsonify({
            "id": existing.id,
            "menu_item_id": existing.menu_item_id,
            "inventory_item_id": existing.inventory_item_id,
            "quantity": existing.quantity,
        })

    recipe = Recipe(
        restaurant_id=restaurant_id,
        menu_item_id=menu_item_id,
        inventory_item_id=inventory_item_id,
        quantity=quantity
    )
    db.session.add(recipe)
    db.session.commit()

    return jsonify({
        "id": recipe.id,
        "menu_item_id": recipe.menu_item_id,
        "inventory_item_id": recipe.inventory_item_id,
        "quantity": recipe.quantity,
    }), 201


@bp.put("/<int:recipe_id>")
@jwt_required()
@require_roles("admin")
def update_recipe(recipe_id: int):
    data = request.get_json(silent=True) or {}
    restaurant_id = get_restaurant_id()
    recipe = Recipe.query.filter_by(id=recipe_id, restaurant_id=restaurant_id).first()
    if not recipe:
        return jsonify({"error": "not_found"}), 404

    quantity = data.get("quantity")
    if quantity is not None:
        recipe.quantity = quantity

    db.session.commit()

    return jsonify({
        "id": recipe.id,
        "menu_item_id": recipe.menu_item_id,
        "inventory_item_id": recipe.inventory_item_id,
        "quantity": recipe.quantity,
    })


@bp.delete("/<int:recipe_id>")
@jwt_required()
@require_roles("admin")
def delete_recipe(recipe_id: int):
    restaurant_id = get_restaurant_id()
    recipe = Recipe.query.filter_by(id=recipe_id, restaurant_id=restaurant_id).first()
    if not recipe:
        return jsonify({"error": "not_found"}), 404

    db.session.delete(recipe)
    db.session.commit()

    return jsonify({"status": "deleted"})


@bp.get("/calculate-price/<int:menu_item_id>")
@jwt_required()
def calculate_price(menu_item_id: int):
    restaurant_id = get_restaurant_id()

    menu_item = MenuItem.query.filter_by(id=menu_item_id, restaurant_id=restaurant_id).first()
    if not menu_item:
        return jsonify({"error": "menu_item_not_found"}), 404

    recipes = Recipe.query.filter_by(menu_item_id=menu_item_id, restaurant_id=restaurant_id).all()
    
    recipe_cost = sum(
        r.quantity * (r.inventory_item.price or 0)
        for r in recipes if r.inventory_item
    )
    
    menu_profit = menu_item.profit or 0
    suggested_price = recipe_cost + menu_profit

    return jsonify({
        "suggested_price": round(suggested_price, 0),
        "recipe_cost": round(recipe_cost, 2),
        "profit": round(menu_profit, 2),
        "total_production_cost": round(recipe_cost, 2),
    })


@bp.post("/update-all-prices")
@jwt_required()
@require_roles("admin")
def update_all_prices():
    restaurant_id = get_restaurant_id()

    menu_items = MenuItem.query.filter_by(restaurant_id=restaurant_id).all()
    
    updated_count = 0
    for menu_item in menu_items:
        recipes = Recipe.query.filter_by(menu_item_id=menu_item.id, restaurant_id=restaurant_id).all()
        
        recipe_cost = sum(
            r.quantity * (r.inventory_item.price or 0)
            for r in recipes if r.inventory_item
        )
        
        menu_profit = menu_item.profit or 0
        suggested_price = recipe_cost + menu_profit
        
        if recipes:
            menu_item.price = round(suggested_price, 0)
            updated_count += 1
    
    db.session.commit()
    
    return jsonify({
        "status": "success",
        "updated_count": updated_count,
        "message": f"Updated {updated_count} menu prices"
    })
