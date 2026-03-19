from datetime import datetime
from ..extensions import db

class KitchenInventory(db.Model):
    __tablename__ = "kitchen_inventory"
    
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    unit = db.Column(db.String(20), nullable=False)  # e.g., kg, liter, pcs
    current_quantity = db.Column(db.Float, default=0.0, nullable=False)
    unit_cost = db.Column(db.Float, default=0.0, nullable=False)
    price = db.Column(db.Float, default=0.0, nullable=False)  # harga per unit
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    restaurant = db.relationship("Restaurant")

class KitchenTransaction(db.Model):
    __tablename__ = "kitchen_transactions"
    
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"), nullable=False)
    inventory_item_id = db.Column(db.Integer, db.ForeignKey("kitchen_inventory.id"), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # "IN" or "OUT"
    quantity = db.Column(db.Float, nullable=False)
    cost = db.Column(db.Float, nullable=True)  # Only for "IN" transactions
    notes = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    inventory_item = db.relationship("KitchenInventory", backref=db.backref('transactions', lazy=True))
    restaurant = db.relationship("Restaurant")
