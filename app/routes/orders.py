from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..extensions import db
from ..models import Order, OrderItem, MenuItem, Payment
from ..services.auth import require_roles, get_restaurant_id

bp = Blueprint("orders", __name__)


def serialize_order(order: Order):
    latest_payment = order.payments[-1] if order.payments else None
    return {
        "id": order.id,
        "restaurant_id": order.restaurant_id,
        "table_no": order.table_no,
        "table_location": order.table_location,
        "status": order.status,
        "created_by": order.created_by,
        "created_at": order.created_at.isoformat(),
        "items": [
            {
                "id": item.id,
                "menu_item_id": item.menu_item_id,
                "qty": item.qty,
                "price_each": item.price_each,
                "line_total": item.qty * item.price_each,
            }
            for item in order.items
        ],
        "total": sum(item.qty * item.price_each for item in order.items),
        "payment": (
            {
                "id": latest_payment.id,
                "method": latest_payment.method,
                "total": latest_payment.total,
                "amount_paid": latest_payment.amount_paid,
                "change": latest_payment.change,
                "paid_at": latest_payment.paid_at.isoformat(),
            }
            if latest_payment
            else None
        ),
    }


@bp.get("")
@jwt_required()
def list_orders():
    status = request.args.get("status")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    restaurant_id = get_restaurant_id()
    query = Order.query.filter_by(restaurant_id=restaurant_id)
    if status:
        query = query.filter_by(status=status)
    
    total = query.count()
    orders = query.order_by(Order.id.desc()).offset((page - 1) * per_page).limit(per_page).all()
    
    return jsonify({
        "orders": [serialize_order(order) for order in orders],
        "total": total,
        "page": page,
        "per_page": per_page,
    })


@bp.get("/<int:order_id>")
@jwt_required()
def get_order(order_id: int):
    restaurant_id = get_restaurant_id()
    order = Order.query.filter_by(id=order_id, restaurant_id=restaurant_id).first()
    if not order:
        return jsonify({"error": "not_found"}), 404
    return jsonify(serialize_order(order))


@bp.post("")
@jwt_required()
@require_roles("admin", "waiter", "kasir")
def create_order():
    data = request.get_json(silent=True) or {}
    table_no = data.get("table_no")
    table_location = data.get("table_location")
    items = data.get("items") or []

    if not table_no or not items:
        return jsonify({"error": "table_no_and_items_required"}), 400

    restaurant_id = get_restaurant_id()
    order = Order(
        table_no=table_no,
        table_location=table_location,
        created_by=get_jwt_identity(),
        restaurant_id=restaurant_id,
    )
    db.session.add(order)

    for item in items:
        menu_item_id = item.get("menu_item_id")
        qty = int(item.get("qty") or 0)
        if not menu_item_id or qty <= 0:
            return jsonify({"error": "invalid_item"}), 400

        menu_item = MenuItem.query.filter_by(id=menu_item_id, restaurant_id=restaurant_id).first()
        if not menu_item or not menu_item.is_active:
            return jsonify({"error": "menu_item_unavailable"}), 400

        order_item = OrderItem(
            order=order,
            menu_item_id=menu_item_id,
            qty=qty,
            price_each=menu_item.price,
        )
        db.session.add(order_item)

    db.session.commit()

    return jsonify(serialize_order(order)), 201


@bp.patch("/<int:order_id>/status")
@jwt_required()
@require_roles("admin", "koki", "kasir")
def update_order_status(order_id: int):
    data = request.get_json(silent=True) or {}
    status = data.get("status")
    if not status:
        return jsonify({"error": "status_required"}), 400

    restaurant_id = get_restaurant_id()
    order = Order.query.filter_by(id=order_id, restaurant_id=restaurant_id).first()
    if not order:
        return jsonify({"error": "not_found"}), 404

    order.status = status
    db.session.commit()

    return jsonify(serialize_order(order))


@bp.patch("/<int:order_id>/pay")
@jwt_required()
@require_roles("admin", "kasir")
def mark_paid(order_id: int):
    restaurant_id = get_restaurant_id()
    order = Order.query.filter_by(id=order_id, restaurant_id=restaurant_id).first()
    if not order:
        return jsonify({"error": "not_found"}), 404

    order.status = "paid"
    db.session.commit()

    return jsonify(serialize_order(order))


@bp.post("/<int:order_id>/payments")
@jwt_required()
@require_roles("admin", "kasir")
def create_payment(order_id: int):
    data = request.get_json(silent=True) or {}
    method = data.get("method")
    amount_paid = data.get("amount_paid")

    if not method or amount_paid is None:
        return jsonify({"error": "method_and_amount_paid_required"}), 400

    restaurant_id = get_restaurant_id()
    order = Order.query.filter_by(id=order_id, restaurant_id=restaurant_id).first()
    if not order:
        return jsonify({"error": "not_found"}), 404

    total = sum(item.qty * item.price_each for item in order.items)
    if total <= 0:
        return jsonify({"error": "invalid_total"}), 400

    amount_paid = int(amount_paid)
    if amount_paid < total:
        return jsonify({"error": "insufficient_payment", "total": total}), 400

    payment = Payment(
        order_id=order.id,
        paid_by=get_jwt_identity(),
        method=method,
        total=total,
        amount_paid=amount_paid,
        change=amount_paid - total,
    )
    db.session.add(payment)

    order.status = "paid"
    db.session.commit()

    return jsonify(serialize_order(order)), 201


@bp.delete("/<int:order_id>")
@jwt_required()
@require_roles("admin")
def delete_order(order_id: int):
    restaurant_id = get_restaurant_id()
    order = Order.query.filter_by(id=order_id, restaurant_id=restaurant_id).first()
    if not order:
        return jsonify({"error": "not_found"}), 404

    db.session.delete(order)
    db.session.commit()

    return jsonify({"status": "deleted"})
