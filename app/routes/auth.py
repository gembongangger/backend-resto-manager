from flask import Blueprint, jsonify, request
import os

from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from ..extensions import db
from ..models import User, Restaurant

bp = Blueprint("auth", __name__)


@bp.post("/bootstrap")
def bootstrap_admin():
    data = request.get_json(silent=True) or {}
    restaurant_name = data.get("restaurant_name")
    username = data.get("username")
    password = data.get("password")
    full_name = data.get("full_name")

    if not restaurant_name or not username or not password:
        return jsonify({"error": "restaurant_name_username_password_required"}), 400

    if Restaurant.query.filter_by(name=restaurant_name).first():
        return jsonify({"error": "restaurant_name_taken"}), 400

    restaurant = Restaurant(name=restaurant_name)
    db.session.add(restaurant)
    db.session.flush()

    user = User(username=username, role="admin", full_name=full_name, restaurant_id=restaurant.id)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({
        "restaurant_id": restaurant.id,
        "restaurant_name": restaurant.name,
        "id": user.id,
        "username": user.username,
        "role": user.role
    }), 201


@bp.post("/bootstrap-superadmin")
def bootstrap_superadmin():
    data = request.get_json(silent=True) or {}
    token = data.get("token")
    username = data.get("username")
    password = data.get("password")
    full_name = data.get("full_name")

    bootstrap_token = os.getenv("SUPERADMIN_BOOTSTRAP_TOKEN")
    if not bootstrap_token or token != bootstrap_token:
        return jsonify({"error": "invalid_bootstrap_token"}), 403

    if not username or not password:
        return jsonify({"error": "username_and_password_required"}), 400

    if User.query.filter_by(username=username, restaurant_id=None).first():
        return jsonify({"error": "username_taken"}), 400

    if User.query.filter_by(role="superadmin").first():
        return jsonify({"error": "superadmin_already_exists"}), 400

    user = User(username=username, role="superadmin", full_name=full_name, restaurant_id=None)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"id": user.id, "username": user.username, "role": user.role}), 201


@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    restaurant_name = data.get("restaurant_name")
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "username_and_password_required"}), 400

    if restaurant_name:
        restaurant = Restaurant.query.filter_by(name=restaurant_name).first()
        if not restaurant or not restaurant.is_active:
            return jsonify({"error": "restaurant_not_found"}), 404

        user = User.query.filter_by(username=username, restaurant_id=restaurant.id).first()
        if not user or not user.check_password(password):
            return jsonify({"error": "invalid_credentials"}), 401

        token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role, "restaurant_id": user.restaurant_id},
        )
        return jsonify({
            "access_token": token,
            "role": user.role,
            "restaurant_id": restaurant.id,
            "restaurant_name": restaurant.name,
        })

    user = User.query.filter_by(username=username, restaurant_id=None, role="superadmin").first()
    if not user or not user.check_password(password):
        return jsonify({"error": "invalid_credentials"}), 401

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role, "restaurant_id": None},
    )
    return jsonify({
        "access_token": token,
        "role": user.role,
        "restaurant_id": None,
        "restaurant_name": None,
    })


@bp.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()
    # Flask-JWT-Extended expects subject to be a string; convert back to int for lookup.
    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        return jsonify({"error": "invalid_token_subject"}), 422
    user = db.session.get(User, user_id_int)
    if not user:
        return jsonify({"error": "not_found"}), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "full_name": user.full_name,
        "restaurant_id": user.restaurant_id,
        "restaurant_name": user.restaurant.name if user.restaurant else None,
    })
