from .health import bp as health_bp
from .auth import bp as auth_bp
from .users import bp as users_bp
from .menu import bp as menu_bp
from .menu_categories import bp as menu_categories_bp
from .orders import bp as orders_bp
from .restaurants import bp as restaurants_bp
from .reports import bp as reports_bp
from .kitchen import bp as kitchen_bp
from .recipes import bp as recipes_bp
from .finance import bp as finance_bp


def register_blueprints(app):
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(menu_bp, url_prefix="/menu")
    app.register_blueprint(menu_categories_bp, url_prefix="/menu-categories")
    app.register_blueprint(orders_bp, url_prefix="/orders")
    app.register_blueprint(restaurants_bp, url_prefix="/restaurants")
    app.register_blueprint(reports_bp, url_prefix="/reports")
    app.register_blueprint(kitchen_bp, url_prefix="/kitchen")
    app.register_blueprint(recipes_bp, url_prefix="/recipes")
    app.register_blueprint(finance_bp, url_prefix="/finance")
