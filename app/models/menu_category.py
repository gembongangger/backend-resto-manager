from datetime import datetime

from ..extensions import db


class MenuCategory(db.Model):
    __tablename__ = "menu_categories"

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    restaurant = db.relationship("Restaurant")
    items = db.relationship("MenuItem", back_populates="category")

    __table_args__ = (
        db.UniqueConstraint("restaurant_id", "name", name="uq_menu_category_restaurant_name"),
    )
