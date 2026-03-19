from ..extensions import db


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey("menu_items.id"), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    price_each = db.Column(db.Integer, nullable=False)

    order = db.relationship("Order", back_populates="items")
    menu_item = db.relationship("MenuItem")
