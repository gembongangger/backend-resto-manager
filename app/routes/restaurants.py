from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

from ..extensions import db
from ..models import Restaurant, User
from ..services.auth import require_roles

bp = Blueprint("restaurants", __name__)


@bp.get("/public")
def public_restaurants():
    restaurants = Restaurant.query.filter_by(is_active=True).order_by(Restaurant.name.asc()).all()
    return jsonify([
        {
            "id": r.id,
            "name": r.name,
        }
        for r in restaurants
    ])


@bp.get("/settings")
@jwt_required()
def get_settings():
    claims = get_jwt()
    user_id = get_jwt_identity()
    restaurant_id = claims.get("restaurant_id")
    
    if restaurant_id is None:
        return jsonify({"error": "restaurant_not_found"}), 404
    
    user = db.session.get(User, int(user_id))
    if not user:
        return jsonify({"error": "user_not_found"}), 404
    
    restaurant = db.session.get(Restaurant, restaurant_id)
    if not restaurant:
        return jsonify({"error": "restaurant_not_found"}), 404
    
    return jsonify({
        "id": restaurant.id,
        "name": restaurant.name,
        "address": restaurant.address or "",
        "phone": restaurant.phone or "",
    })


@bp.put("/settings")
@jwt_required()
@require_roles("admin")
def update_settings():
    claims = get_jwt()
    user_id = get_jwt_identity()
    restaurant_id = claims.get("restaurant_id")
    
    if restaurant_id is None:
        return jsonify({"error": "restaurant_not_found"}), 404
    
    user = db.session.get(User, int(user_id))
    if not user:
        return jsonify({"error": "user_not_found"}), 404
    
    restaurant = db.session.get(Restaurant, user.restaurant_id)
    if not restaurant:
        return jsonify({"error": "restaurant_not_found"}), 404
    
    data = request.get_json(silent=True) or {}
    
    name = data.get("name")
    if name is not None:
        restaurant.name = name
    
    address = data.get("address")
    if address is not None:
        restaurant.address = address
    
    phone = data.get("phone")
    if phone is not None:
        restaurant.phone = phone
    
    db.session.commit()
    
    return jsonify({
        "id": restaurant.id,
        "name": restaurant.name,
        "address": restaurant.address or "",
        "phone": restaurant.phone or "",
    })


@bp.get("")
@jwt_required()
@require_roles("superadmin")
def list_restaurants():
    include_admins = request.args.get("include_admins", "false").lower() == "true"
    restaurants = Restaurant.query.order_by(Restaurant.id.asc()).all()
    
    result = []
    for r in restaurants:
        resto_data = {
            "id": r.id,
            "name": r.name,
            "address": getattr(r, 'address', '') or '',
            "phone": getattr(r, 'phone', '') or '',
            "is_active": r.is_active,
            "created_at": r.created_at.isoformat(),
        }
        
        if include_admins:
            admins = User.query.filter_by(restaurant_id=r.id, role="admin").all()
            resto_data["admins"] = [
                {
                    "id": u.id,
                    "username": u.username,
                    "full_name": u.full_name,
                    "is_active": u.is_active,
                    "created_at": u.created_at.isoformat() if u.created_at else None,
                }
                for u in admins
            ]
        
        result.append(resto_data)
    
    return jsonify(result)


@bp.get("/<int:restaurant_id>")
@jwt_required()
@require_roles("superadmin")
def get_restaurant(restaurant_id: int):
    restaurant = db.session.get(Restaurant, restaurant_id)
    if not restaurant:
        return jsonify({"error": "not_found"}), 404
    return jsonify({
        "id": restaurant.id,
        "name": restaurant.name,
        "address": restaurant.address or "",
        "phone": restaurant.phone or "",
    })


@bp.post("")
@jwt_required()
@require_roles("superadmin")
def create_restaurant():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    if not name:
        return jsonify({"error": "name_required"}), 400

    if Restaurant.query.filter_by(name=name).first():
        return jsonify({"error": "name_taken"}), 400

    restaurant = Restaurant(name=name)
    db.session.add(restaurant)
    db.session.commit()

    return jsonify({"id": restaurant.id, "name": restaurant.name, "is_active": restaurant.is_active}), 201


@bp.put("/<int:restaurant_id>")
@jwt_required()
@require_roles("superadmin")
def update_restaurant(restaurant_id: int):
    data = request.get_json(silent=True) or {}
    restaurant = db.session.get(Restaurant, restaurant_id)
    if not restaurant:
        return jsonify({"error": "not_found"}), 404

    name = data.get("name")
    if name is not None:
        if Restaurant.query.filter(Restaurant.name == name, Restaurant.id != restaurant_id).first():
            return jsonify({"error": "name_taken"}), 400
        restaurant.name = name

    address = data.get("address")
    if address is not None:
        restaurant.address = address

    phone = data.get("phone")
    if phone is not None:
        restaurant.phone = phone

    is_active = data.get("is_active")
    if is_active is not None:
        restaurant.is_active = bool(is_active)

    db.session.commit()

    return jsonify({
        "id": restaurant.id,
        "name": restaurant.name,
        "address": restaurant.address or "",
        "phone": restaurant.phone or "",
        "is_active": restaurant.is_active,
    })


@bp.put("/<int:restaurant_id>/active")
@jwt_required()
@require_roles("superadmin")
def toggle_active(restaurant_id: int):
    data = request.get_json(silent=True) or {}
    restaurant = db.session.get(Restaurant, restaurant_id)
    if not restaurant:
        return jsonify({"error": "not_found"}), 404

    restaurant.is_active = bool(data.get("is_active", True))
    db.session.commit()

    return jsonify({
        "id": restaurant.id,
        "name": restaurant.name,
        "is_active": restaurant.is_active,
    })


@bp.delete("/<int:restaurant_id>")
@jwt_required()
@require_roles("superadmin")
def delete_restaurant(restaurant_id: int):
    restaurant = db.session.get(Restaurant, restaurant_id)
    if not restaurant:
        return jsonify({"error": "not_found"}), 404
    
    User.query.filter_by(restaurant_id=restaurant_id).delete()
    db.session.delete(restaurant)
    db.session.commit()
    
    return jsonify({"status": "deleted", "id": restaurant_id})


@bp.post("/<int:restaurant_id>/reset-admin-password")
@jwt_required()
@require_roles("superadmin")
def reset_admin_password(restaurant_id: int):
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    new_password = data.get("new_password")

    if not username or not new_password:
        return jsonify({"error": "username_and_new_password_required"}), 400

    restaurant = db.session.get(Restaurant, restaurant_id)
    if not restaurant:
        return jsonify({"error": "restaurant_not_found"}), 404

    admin_user = User.query.filter_by(
        username=username,
        restaurant_id=restaurant_id,
        role="admin",
    ).first()
    if not admin_user:
        return jsonify({"error": "admin_user_not_found"}), 404

    admin_user.set_password(new_password)
    db.session.commit()

    return jsonify({"status": "password_reset", "user_id": admin_user.id, "username": admin_user.username})


@bp.get("/<int:restaurant_id>/admins")
@jwt_required()
@require_roles("superadmin")
def list_admins(restaurant_id: int):
    restaurant = db.session.get(Restaurant, restaurant_id)
    if not restaurant:
        return jsonify({"error": "restaurant_not_found"}), 404
    
    admins = User.query.filter_by(restaurant_id=restaurant_id, role="admin").all()
    return jsonify([
        {
            "id": u.id,
            "username": u.username,
            "full_name": u.full_name,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in admins
    ])


@bp.post("/<int:restaurant_id>/admins")
@jwt_required()
@require_roles("superadmin")
def create_admin(restaurant_id: int):
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")
    full_name = data.get("full_name")

    if not username or not password:
        return jsonify({"error": "username_and_password_required"}), 400

    restaurant = db.session.get(Restaurant, restaurant_id)
    if not restaurant:
        return jsonify({"error": "restaurant_not_found"}), 404

    if User.query.filter_by(restaurant_id=restaurant_id, username=username).first():
        return jsonify({"error": "username_taken"}), 400

    admin = User(
        restaurant_id=restaurant_id,
        username=username,
        role="admin",
        full_name=full_name or None,
    )
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()

    return jsonify({
        "id": admin.id,
        "username": admin.username,
        "full_name": admin.full_name,
        "is_active": admin.is_active,
        "created_at": admin.created_at.isoformat(),
    }), 201


@bp.put("/<int:restaurant_id>/admins/<int:admin_id>")
@jwt_required()
@require_roles("superadmin")
def update_admin(restaurant_id: int, admin_id: int):
    data = request.get_json(silent=True) or {}
    admin = User.query.filter_by(id=admin_id, restaurant_id=restaurant_id, role="admin").first()
    if not admin:
        return jsonify({"error": "admin_not_found"}), 404

    username = data.get("username")
    if username is not None:
        existing = User.query.filter(
            User.restaurant_id == restaurant_id,
            User.username == username,
            User.id != admin_id
        ).first()
        if existing:
            return jsonify({"error": "username_taken"}), 400
        admin.username = username

    password = data.get("password")
    if password:
        admin.set_password(password)

    full_name = data.get("full_name")
    if full_name is not None:
        admin.full_name = full_name or None

    is_active = data.get("is_active")
    if is_active is not None:
        admin.is_active = bool(is_active)

    db.session.commit()

    return jsonify({
        "id": admin.id,
        "username": admin.username,
        "full_name": admin.full_name,
        "is_active": admin.is_active,
        "created_at": admin.created_at.isoformat() if admin.created_at else None,
    })


@bp.delete("/<int:restaurant_id>/admins/<int:admin_id>")
@jwt_required()
@require_roles("superadmin")
def delete_admin(restaurant_id: int, admin_id: int):
    admin = User.query.filter_by(id=admin_id, restaurant_id=restaurant_id, role="admin").first()
    if not admin:
        return jsonify({"error": "admin_not_found"}), 404

    db.session.delete(admin)
    db.session.commit()

    return jsonify({"status": "deleted", "id": admin_id})
