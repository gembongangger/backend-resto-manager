from datetime import datetime

from ..extensions import db


class MenuItem(db.Model):
    __tablename__ = "menu_items"

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("menu_categories.id"), nullable=True)
    price = db.Column(db.Integer, nullable=False)
    profit = db.Column(db.Integer, nullable=False, default=0)
    image_url = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    restaurant = db.relationship("Restaurant")
    category = db.relationship("MenuCategory", back_populates="items")
    recipes = db.relationship("Recipe", backref="menu_item", cascade="all, delete", lazy="dynamic")
