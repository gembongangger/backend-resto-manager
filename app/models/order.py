from datetime import datetime

from ..extensions import db


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"), nullable=False)
    table_no = db.Column(db.String(20), nullable=False)
    table_location = db.Column(db.String(120))
    status = db.Column(
        db.String(20),
        default="pending",
        nullable=False,
    )
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    items = db.relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = db.relationship("Payment", back_populates="order", cascade="all, delete-orphan")
    creator = db.relationship("User")
    restaurant = db.relationship("Restaurant")
