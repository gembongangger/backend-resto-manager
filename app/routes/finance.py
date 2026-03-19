from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from ..extensions import db
from ..models import FinanceEntry, User
from ..services.auth import get_restaurant_id, require_roles

bp = Blueprint("finance", __name__)


def parse_entry_date(value: str | None):
    if not value:
        return datetime.utcnow()

    try:
        if len(value) == 10:
            return datetime.fromisoformat(value + "T00:00:00")
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def serialize_entry(entry: FinanceEntry):
    creator_name = None
    if entry.creator:
        creator_name = entry.creator.full_name or entry.creator.username

    return {
        "id": entry.id,
        "restaurant_id": entry.restaurant_id,
        "created_by": entry.created_by,
        "created_by_name": creator_name,
        "title": entry.title,
        "entry_type": entry.entry_type,
        "amount": entry.amount,
        "notes": entry.notes or "",
        "entry_date": entry.entry_date.isoformat(),
        "created_at": entry.created_at.isoformat(),
        "updated_at": entry.updated_at.isoformat(),
    }


@bp.get("/entries")
@jwt_required()
@require_roles("admin", "kasir")
def list_entries():
    restaurant_id = get_restaurant_id()
    entry_type = request.args.get("type")
    start_raw = request.args.get("start")
    end_raw = request.args.get("end")

    query = FinanceEntry.query.filter_by(restaurant_id=restaurant_id)

    if entry_type:
        query = query.filter(FinanceEntry.entry_type == entry_type)

    if start_raw:
        start_dt = parse_entry_date(start_raw)
        if not start_dt:
            return jsonify({"error": "invalid_start_date"}), 400
        query = query.filter(FinanceEntry.entry_date >= start_dt)

    if end_raw:
        end_dt = parse_entry_date(end_raw)
        if not end_dt:
            return jsonify({"error": "invalid_end_date"}), 400
        if len(end_raw) == 10:
            end_dt = end_dt + timedelta(days=1) - timedelta(microseconds=1)
        query = query.filter(FinanceEntry.entry_date <= end_dt)

    entries = query.order_by(FinanceEntry.entry_date.desc(), FinanceEntry.id.desc()).all()
    return jsonify([serialize_entry(entry) for entry in entries])


@bp.post("/entries")
@jwt_required()
@require_roles("admin")
def create_entry():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    entry_type = data.get("entry_type")
    amount = data.get("amount")
    notes = data.get("notes")
    entry_date = parse_entry_date(data.get("entry_date"))

    if not title:
        return jsonify({"error": "title_required"}), 400
    if entry_type not in {"salary", "owner_draw", "expense"}:
        return jsonify({"error": "invalid_entry_type"}), 400
    if entry_date is None:
        return jsonify({"error": "invalid_entry_date"}), 400

    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return jsonify({"error": "invalid_amount"}), 400

    if amount <= 0:
        return jsonify({"error": "amount_must_be_positive"}), 400

    user = db.session.get(User, get_jwt_identity())
    restaurant_id = get_restaurant_id()

    entry = FinanceEntry(
        restaurant_id=restaurant_id,
        created_by=user.id if user else None,
        title=title,
        entry_type=entry_type,
        amount=amount,
        notes=notes,
        entry_date=entry_date,
    )
    db.session.add(entry)
    db.session.commit()
    return jsonify(serialize_entry(entry)), 201


@bp.put("/entries/<int:entry_id>")
@jwt_required()
@require_roles("admin")
def update_entry(entry_id: int):
    restaurant_id = get_restaurant_id()
    entry = FinanceEntry.query.filter_by(id=entry_id, restaurant_id=restaurant_id).first()
    if not entry:
        return jsonify({"error": "not_found"}), 404

    data = request.get_json(silent=True) or {}

    if "title" in data:
        title = (data.get("title") or "").strip()
        if not title:
            return jsonify({"error": "title_required"}), 400
        entry.title = title

    if "entry_type" in data:
        entry_type = data.get("entry_type")
        if entry_type not in {"salary", "owner_draw", "expense"}:
            return jsonify({"error": "invalid_entry_type"}), 400
        entry.entry_type = entry_type

    if "amount" in data:
        try:
            amount = float(data.get("amount"))
        except (TypeError, ValueError):
            return jsonify({"error": "invalid_amount"}), 400
        if amount <= 0:
            return jsonify({"error": "amount_must_be_positive"}), 400
        entry.amount = amount

    if "notes" in data:
        entry.notes = data.get("notes")

    if "entry_date" in data:
        entry_date = parse_entry_date(data.get("entry_date"))
        if entry_date is None:
            return jsonify({"error": "invalid_entry_date"}), 400
        entry.entry_date = entry_date

    db.session.commit()
    return jsonify(serialize_entry(entry))


@bp.delete("/entries/<int:entry_id>")
@jwt_required()
@require_roles("admin")
def delete_entry(entry_id: int):
    restaurant_id = get_restaurant_id()
    entry = FinanceEntry.query.filter_by(id=entry_id, restaurant_id=restaurant_id).first()
    if not entry:
        return jsonify({"error": "not_found"}), 404

    db.session.delete(entry)
    db.session.commit()
    return jsonify({"status": "deleted"})
