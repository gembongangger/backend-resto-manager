from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from ..extensions import db
from ..models import MenuCategory
from ..services.auth import require_roles, get_restaurant_id

bp = Blueprint("menu_categories", __name__)


@bp.get("")
@jwt_required()
def list_categories():
    restaurant_id = get_restaurant_id()
    categories = (
        MenuCategory.query.filter_by(restaurant_id=restaurant_id)
        .order_by(MenuCategory.name.asc())
        .all()
    )
    return jsonify([
        {"id": c.id, "name": c.name}
        for c in categories
    ])


@bp.post("")
@jwt_required()
@require_roles("admin")
def create_category():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name_required"}), 400

    restaurant_id = get_restaurant_id()
    existing = MenuCategory.query.filter_by(restaurant_id=restaurant_id, name=name).first()
    if existing:
        return jsonify({"error": "name_taken"}), 400

    category = MenuCategory(name=name, restaurant_id=restaurant_id)
    db.session.add(category)
    db.session.commit()

    return jsonify({"id": category.id, "name": category.name}), 201


@bp.delete("/<int:category_id>")
@jwt_required()
@require_roles("admin")
def delete_category(category_id: int):
    restaurant_id = get_restaurant_id()
    category = MenuCategory.query.filter_by(id=category_id, restaurant_id=restaurant_id).first()
    if not category:
        return jsonify({"error": "not_found"}), 404

    # Prevent delete if still used by menu items
    if category.items:
        return jsonify({"error": "category_in_use"}), 400

    db.session.delete(category)
    db.session.commit()

    return jsonify({"status": "deleted"})
