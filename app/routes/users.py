from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..extensions import db
from ..models import User
from ..services.auth import require_roles, get_restaurant_id

bp = Blueprint("users", __name__)

VALID_ROLES = {"admin", "kasir", "koki", "waiter"}


@bp.get("")
@jwt_required()
@require_roles("admin")
def list_users():
    restaurant_id = get_restaurant_id()
    users = User.query.filter_by(restaurant_id=restaurant_id).order_by(User.id.asc()).all()
    return jsonify([
        {
            "id": u.id,
            "username": u.username,
            "role": u.role,
            "full_name": u.full_name,
            "created_at": u.created_at.isoformat(),
        }
        for u in users
    ])


@bp.post("")
@jwt_required()
@require_roles("admin")
def create_user():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")
    role = data.get("role")
    full_name = data.get("full_name")

    if not username or not password or not role:
        return jsonify({"error": "username_password_role_required"}), 400
    if role not in VALID_ROLES:
        return jsonify({"error": "invalid_role"}), 400
    restaurant_id = get_restaurant_id()
    if User.query.filter_by(username=username, restaurant_id=restaurant_id).first():
        return jsonify({"error": "username_taken"}), 400

    user = User(username=username, role=role, full_name=full_name, restaurant_id=restaurant_id)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"id": user.id, "username": user.username, "role": user.role}), 201


@bp.put("/<int:user_id>")
@jwt_required()
@require_roles("admin")
def update_user(user_id: int):
    data = request.get_json(silent=True) or {}
    restaurant_id = get_restaurant_id()
    user = User.query.filter_by(id=user_id, restaurant_id=restaurant_id).first()
    if not user:
        return jsonify({"error": "not_found"}), 404

    role = data.get("role")
    if role:
        if role not in VALID_ROLES:
            return jsonify({"error": "invalid_role"}), 400
        user.role = role

    full_name = data.get("full_name")
    if full_name is not None:
        user.full_name = full_name

    password = data.get("password")
    if password:
        user.set_password(password)

    db.session.commit()

    return jsonify({"id": user.id, "username": user.username, "role": user.role})


@bp.delete("/<int:user_id>")
@jwt_required()
@require_roles("admin")
def delete_user(user_id: int):
    current_user_id = get_jwt_identity()
    if current_user_id == user_id:
        return jsonify({"error": "cannot_delete_self"}), 400

    restaurant_id = get_restaurant_id()
    user = User.query.filter_by(id=user_id, restaurant_id=restaurant_id).first()
    if not user:
        return jsonify({"error": "not_found"}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({"status": "deleted"})
