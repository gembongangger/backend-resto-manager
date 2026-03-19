from datetime import datetime
from passlib.hash import pbkdf2_sha256

from ..extensions import db


class User(db.Model):
    __tablename__ = "users"
    __table_args__ = (
        db.UniqueConstraint("restaurant_id", "username", name="uq_users_restaurant_username"),
    )

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"), nullable=True)
    username = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    full_name = db.Column(db.String(120))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    restaurant = db.relationship("Restaurant")

    def set_password(self, password: str) -> None:
        self.password_hash = pbkdf2_sha256.hash(password)

    def check_password(self, password: str) -> bool:
        return pbkdf2_sha256.verify(password, self.password_hash)
