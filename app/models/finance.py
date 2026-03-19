from datetime import datetime

from ..extensions import db


class FinanceEntry(db.Model):
    __tablename__ = "finance_entries"
    __table_args__ = (
        db.CheckConstraint(
            "entry_type in ('salary', 'owner_draw', 'expense')",
            name="ck_finance_entries_entry_type",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    title = db.Column(db.String(120), nullable=False)
    entry_type = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    notes = db.Column(db.String(255))
    entry_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    restaurant = db.relationship("Restaurant")
    creator = db.relationship("User")
