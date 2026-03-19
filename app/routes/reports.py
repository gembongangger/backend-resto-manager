from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from ..extensions import db
from ..models import FinanceEntry, KitchenTransaction, Order, Payment, Recipe
from ..services.auth import require_roles, get_restaurant_id

bp = Blueprint("reports", __name__)


def parse_date(value: str):
    try:
        # Handle cases like '2026-03-16' (date-only) by appending 'T00:00:00'
        if len(value) == 10:
            value = value + "T00:00:00"
        return datetime.fromisoformat(value)
    except ValueError:
        return None


@bp.get("/sales")
@jwt_required()
@require_roles("admin", "kasir")
def sales_report():
    start_raw = request.args.get("start")
    end_raw = request.args.get("end")
    if not start_raw or not end_raw:
        return jsonify({"error": "start_and_end_required"}), 400

    start_dt = parse_date(start_raw)
    end_dt = parse_date(end_raw)
    if not start_dt or not end_dt:
        return jsonify({"error": "invalid_datetime_format"}), 400

    # Make end inclusive for date-only inputs by adding 1 day minus 1 microsecond.
    if len(end_raw) == 10:
        end_dt = end_dt + timedelta(days=1) - timedelta(microseconds=1)

    if end_dt < start_dt:
        return jsonify({"error": "end_before_start"}), 400

    restaurant_id = get_restaurant_id()
    
    # Calculate Kitchen Expenses
    kitchen_tx_query = (
        db.session.query(KitchenTransaction)
        .filter(KitchenTransaction.restaurant_id == restaurant_id)
        .filter(KitchenTransaction.type == "IN")
        .filter(KitchenTransaction.created_at >= start_dt, KitchenTransaction.created_at <= end_dt)
    )
    kitchen_txs = kitchen_tx_query.all()
    kitchen_expenses = sum(tx.cost or 0 for tx in kitchen_txs)

    finance_entries = (
        db.session.query(FinanceEntry)
        .filter(FinanceEntry.restaurant_id == restaurant_id)
        .filter(FinanceEntry.entry_date >= start_dt, FinanceEntry.entry_date <= end_dt)
        .order_by(FinanceEntry.entry_date.asc())
        .all()
    )
    salary_expenses = sum(entry.amount for entry in finance_entries if entry.entry_type == "salary")
    operational_expenses = sum(entry.amount for entry in finance_entries if entry.entry_type == "expense")
    owner_draw_total = sum(entry.amount for entry in finance_entries if entry.entry_type == "owner_draw")
    finance_expenses = salary_expenses + operational_expenses

    query = (
        db.session.query(Payment)
        .join(Order, Payment.order_id == Order.id)
        .filter(Order.restaurant_id == restaurant_id)
        .filter(Payment.paid_at >= start_dt, Payment.paid_at <= end_dt)
    )

    payments = query.order_by(Payment.paid_at.asc()).all()

    total_sales = sum(p.total for p in payments)
    total_paid = sum(p.amount_paid for p in payments)
    total_change = sum(p.change for p in payments)

    # Compute cost/profit and items sold based on orders paid in this period.
    order_ids = [p.order_id for p in payments]
    items_sold_map = {}
    total_cost = 0
    if order_ids:
        orders = Order.query.filter(Order.id.in_(order_ids)).all()
        for order in orders:
            for item in order.items:
                menu_item = item.menu_item
                menu_name = menu_item.name if menu_item else "Unknown"
                
                # Calculate cost from recipes (ingredients)
                recipes = Recipe.query.filter_by(menu_item_id=item.menu_item_id).all()
                recipe_cost = sum(
                    r.quantity * (r.inventory_item.price or 0)
                    for r in recipes if r.inventory_item
                )
                
                revenue = item.qty * item.price_each
                cost = item.qty * recipe_cost
                total_cost += cost
                entry = items_sold_map.get(item.menu_item_id)
                if not entry:
                    entry = {
                        "menu_item_id": item.menu_item_id,
                        "name": menu_name,
                        "qty": 0,
                        "revenue": 0,
                        "cost": 0,
                        "profit": 0,
                    }
                    items_sold_map[item.menu_item_id] = entry
                entry["qty"] += item.qty
                entry["revenue"] += revenue
                entry["cost"] += cost
                entry["profit"] += revenue - cost

    items_sold = sorted(items_sold_map.values(), key=lambda x: x["revenue"], reverse=True)
    total_profit = total_sales - total_cost
    net_operating_profit = total_profit - kitchen_expenses - finance_expenses
    net_cash_after_owner_draw = net_operating_profit - owner_draw_total

    by_method = {}
    for p in payments:
        by_method.setdefault(p.method, {"count": 0, "total": 0})
        by_method[p.method]["count"] += 1
        by_method[p.method]["total"] += p.total

    return jsonify({
        "start": start_dt.isoformat(),
        "end": end_dt.isoformat(),
        "count": len(payments),
        "total_sales": total_sales,
        "total_paid": total_paid,
        "total_change": total_change,
        "total_cost": total_cost,
        "total_profit": total_profit,
        "kitchen_expenses": kitchen_expenses,
        "salary_expenses": salary_expenses,
        "operational_expenses": operational_expenses,
        "finance_expenses": finance_expenses,
        "owner_draw_total": owner_draw_total,
        "net_profit": net_operating_profit,
        "net_operating_profit": net_operating_profit,
        "net_cash_after_owner_draw": net_cash_after_owner_draw,
        "by_method": by_method,
        "items_sold": items_sold,
    })
