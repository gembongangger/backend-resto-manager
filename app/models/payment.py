from datetime import datetime

from ..extensions import db


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    paid_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    method = db.Column(db.String(30), nullable=False)
    total = db.Column(db.Integer, nullable=False)
    amount_paid = db.Column(db.Integer, nullable=False)
    change = db.Column(db.Integer, nullable=False)
    paid_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    order = db.relationship("Order", back_populates="payments")
    cashier = db.relationship("User")
