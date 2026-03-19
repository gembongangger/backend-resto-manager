from datetime import datetime

from ..extensions import db


class Recipe(db.Model):
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey("menu_items.id"), nullable=False)
    inventory_item_id = db.Column(db.Integer, db.ForeignKey("kitchen_inventory.id"), nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    restaurant = db.relationship("Restaurant")
    inventory_item = db.relationship("KitchenInventory", backref="recipes")
