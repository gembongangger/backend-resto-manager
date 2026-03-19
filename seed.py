from app import create_app
from app.extensions import db
from app.models import Restaurant, User


def get_or_create_restaurant(name: str) -> Restaurant:
    restaurant = Restaurant.query.filter_by(name=name).first()
    if restaurant:
        return restaurant
    restaurant = Restaurant(name=name)
    db.session.add(restaurant)
    db.session.flush()
    return restaurant


def get_or_create_user(username: str, role: str, restaurant_id):
    user = User.query.filter_by(username=username, role=role, restaurant_id=restaurant_id).first()
    if user:
        return user
    user = User(username=username, role=role, restaurant_id=restaurant_id)
    user.set_password(username)
    db.session.add(user)
    return user


def main():
    app = create_app()
    with app.app_context():
        db.create_all()
        resto_a = get_or_create_restaurant("Resto A")
        resto_b = get_or_create_restaurant("Resto B")

        # Superadmin (no restaurant)
        get_or_create_user("superadmin", "superadmin", None)

        # Resto A users
        get_or_create_user("admin_a", "admin", resto_a.id)
        get_or_create_user("kasir_a", "kasir", resto_a.id)
        get_or_create_user("koki_a", "koki", resto_a.id)
        get_or_create_user("waiter_a", "waiter", resto_a.id)

        # Resto B users
        get_or_create_user("admin_b", "admin", resto_b.id)
        get_or_create_user("kasir_b", "kasir", resto_b.id)
        get_or_create_user("koki_b", "koki", resto_b.id)
        get_or_create_user("waiter_b", "waiter", resto_b.id)

        db.session.commit()
        print("Seeded sample users for Resto A, Resto B, and superadmin.")


if __name__ == "__main__":
    main()
