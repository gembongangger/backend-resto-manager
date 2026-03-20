from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func

from ..extensions import db
from ..models import KitchenInventory, KitchenTransaction
from ..services.auth import require_roles, get_restaurant_id

bp = Blueprint("kitchen", __name__)


@bp.post("/recalculate-prices")
@jwt_required()
@require_roles("admin")
def recalculate_prices():
    restaurant_id = get_restaurant_id()
    inventory_items = KitchenInventory.query.filter_by(restaurant_id=restaurant_id).all()
    
    updated_count = 0
    for item in inventory_items:
        latest_tx = KitchenTransaction.query.filter_by(
            inventory_item_id=item.id,
            type="IN"
        ).order_by(KitchenTransaction.created_at.desc()).first()
        
        if latest_tx and latest_tx.cost and latest_tx.quantity and latest_tx.quantity > 0:
            new_price = latest_tx.cost / latest_tx.quantity
            item.price = new_price
            item.unit_cost = new_price
            updated_count += 1
    
    db.session.commit()
    
    return jsonify({
        "status": "success",
        "updated_count": updated_count,
        "message": f"Updated {updated_count} item prices from latest transactions"
    })


def serialize_inventory(item: KitchenInventory):
    return {
        "id": item.id,
        "restaurant_id": item.restaurant_id,
        "name": item.name,
        "unit": item.unit,
        "current_quantity": item.current_quantity,
        "unit_cost": item.unit_cost,
        "price": item.price,
        "updated_at": item.updated_at.isoformat(),
    }

def serialize_transaction(tx: KitchenTransaction):
    return {
        "id": tx.id,
        "inventory_item_id": tx.inventory_item_id,
        "inventory_item_name": tx.inventory_item.name,
        "type": tx.type,
        "quantity": tx.quantity,
        "cost": tx.cost,
        "notes": tx.notes,
        "created_at": tx.created_at.isoformat(),
    }

@bp.get("/inventory")
@jwt_required()
def list_inventory():
    restaurant_id = get_restaurant_id()
    items = KitchenInventory.query.filter_by(restaurant_id=restaurant_id).all()
    return jsonify([serialize_inventory(i) for i in items])

@bp.post("/inventory")
@jwt_required()
@require_roles("admin")
def create_inventory_item():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    unit = data.get("unit")
    
    if not name or not unit:
        return jsonify({"error": "name_and_unit_required"}), 400

    restaurant_id = get_restaurant_id()
    item = KitchenInventory(
        name=name,
        unit=unit,
        restaurant_id=restaurant_id
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(serialize_inventory(item)), 201


@bp.put("/inventory/<int:item_id>")
@jwt_required()
@require_roles("admin")
def update_inventory_item(item_id: int):
    data = request.get_json(silent=True) or {}
    restaurant_id = get_restaurant_id()
    item = KitchenInventory.query.filter_by(id=item_id, restaurant_id=restaurant_id).first()
    if not item:
        return jsonify({"error": "not_found"}), 404

    name = data.get("name")
    if name is not None:
        item.name = name

    unit = data.get("unit")
    if unit is not None:
        item.unit = unit

    unit_cost = data.get("unit_cost")
    if unit_cost is not None:
        item.unit_cost = float(unit_cost)

    current_quantity = data.get("current_quantity")
    if current_quantity is not None:
        item.current_quantity = float(current_quantity)

    db.session.commit()
    return jsonify(serialize_inventory(item))


@bp.delete("/inventory/<int:item_id>")
@jwt_required()
@require_roles("admin")
def delete_inventory_item(item_id: int):
    restaurant_id = get_restaurant_id()
    item = KitchenInventory.query.filter_by(id=item_id, restaurant_id=restaurant_id).first()
    if not item:
        return jsonify({"error": "not_found"}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({"status": "deleted"})


@bp.post("/transactions")
@jwt_required()
@require_roles("admin", "koki")
def create_transaction():
    data = request.get_json(silent=True) or {}
    item_id = data.get("inventory_item_id")
    tx_type = data.get("type") # "IN" or "OUT"
    quantity = float(data.get("quantity") or 0)
    cost = data.get("cost")
    notes = data.get("notes")

    if not item_id or tx_type not in ["IN", "OUT"] or quantity <= 0:
        return jsonify({"error": "invalid_transaction_data"}), 400

    restaurant_id = get_restaurant_id()
    item = KitchenInventory.query.filter_by(id=item_id, restaurant_id=restaurant_id).first()
    if not item:
        return jsonify({"error": "item_not_found"}), 404

    # Update inventory quantity
    if tx_type == "IN":
        item.current_quantity += quantity
        
        # Calculate new weighted average price
        if cost and float(cost) > 0:
            new_cost = float(cost)
            new_quantity = quantity
            new_price_per_unit = new_cost / new_quantity
            
            # Weighted average: (old_price × old_qty + new_price × new_qty) / (old_qty + new_qty)
            if item.current_quantity > 0:
                old_value = (item.price or 0) * (item.current_quantity - new_quantity)
                new_value = new_price_per_unit * new_quantity
                item.price = (old_value + new_value) / item.current_quantity
                item.unit_cost = item.price
        
        transaction_cost = float(cost) if cost else None
    else:
        if item.current_quantity < quantity:
            return jsonify({"error": "insufficient_quantity"}), 400
        item.current_quantity -= quantity
        
        # Record cost based on latest price for OUT transactions
        transaction_cost = item.price * quantity if item.price else None

    transaction = KitchenTransaction(
        restaurant_id=restaurant_id,
        inventory_item_id=item_id,
        type=tx_type,
        quantity=quantity,
        cost=transaction_cost,
        notes=notes
    )
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify(serialize_transaction(transaction)), 201

@bp.get("/transactions")
@jwt_required()
def list_transactions():
    restaurant_id = get_restaurant_id()
    txs = KitchenTransaction.query.filter_by(restaurant_id=restaurant_id).order_by(KitchenTransaction.id.desc()).all()
    return jsonify([serialize_transaction(tx) for tx in txs])


@bp.put("/transactions/<int:tx_id>")
@jwt_required()
@require_roles("admin")
def update_transaction(tx_id: int):
    data = request.get_json(silent=True) or {}
    restaurant_id = get_restaurant_id()
    tx = KitchenTransaction.query.filter_by(id=tx_id, restaurant_id=restaurant_id).first()
    if not tx:
        return jsonify({"error": "not_found"}), 404

    tx_type = data.get("type")
    quantity = data.get("quantity")
    cost = data.get("cost")
    notes = data.get("notes")

    # Get the inventory item for price recalculation
    item = KitchenInventory.query.filter_by(id=tx.inventory_item_id, restaurant_id=restaurant_id).first()
    if not item:
        return jsonify({"error": "item_not_found"}), 404

    # First, reverse the old transaction effect on inventory
    if tx.type == "IN":
        item.current_quantity -= tx.quantity
    else:  # OUT
        item.current_quantity += tx.quantity

    # Update transaction fields
    new_quantity = tx.quantity
    new_cost = tx.cost
    
    if quantity is not None:
        new_quantity = float(quantity)
        if new_quantity <= 0:
            return jsonify({"error": "invalid_quantity"}), 400

    if cost is not None and tx.type == "IN":
        new_cost = float(cost)

    if notes is not None:
        tx.notes = notes

    # Update transaction with new values
    tx.quantity = new_quantity
    if tx.type == "IN" and cost is not None:
        tx.cost = new_cost

    # Now apply the new transaction effect and recalculate price
    if tx.type == "IN":
        item.current_quantity += new_quantity

        # Recalculate weighted average price for IN transactions
        if new_cost and new_quantity > 0:
            new_price_per_unit = new_cost / new_quantity

            # Weighted average: (old_price × old_qty + new_price × new_qty) / (old_qty + new_qty)
            if item.current_quantity > 0:
                # Get all IN transactions for this item except current one
                other_in_txs = KitchenTransaction.query.filter_by(
                    inventory_item_id=item.id,
                    type="IN"
                ).filter(KitchenTransaction.id != tx_id).all()

                # Calculate total value and quantity from other transactions
                total_value = 0.0
                total_qty = 0.0
                for other_tx in other_in_txs:
                    if other_tx.cost and other_tx.quantity:
                        other_price_per_unit = other_tx.cost / other_tx.quantity
                        total_value += other_price_per_unit * other_tx.quantity
                        total_qty += other_tx.quantity

                # Add current transaction value
                total_value += new_cost
                total_qty += new_quantity

                # New weighted average price
                if total_qty > 0:
                    item.price = total_value / total_qty
                    item.unit_cost = item.price
    else:  # OUT transaction
        if item.current_quantity < new_quantity:
            # Reverse back the old effect since we can't apply new one
            item.current_quantity -= tx.quantity
            return jsonify({"error": "insufficient_quantity"}), 400
        item.current_quantity -= new_quantity

    db.session.commit()
    return jsonify(serialize_transaction(tx))


@bp.delete("/transactions/<int:tx_id>")
@jwt_required()
@require_roles("admin")
def delete_transaction(tx_id: int):
    restaurant_id = get_restaurant_id()
    tx = KitchenTransaction.query.filter_by(id=tx_id, restaurant_id=restaurant_id).first()
    if not tx:
        return jsonify({"error": "not_found"}), 404

    db.session.delete(tx)
    db.session.commit()
    return jsonify({"status": "deleted"})
