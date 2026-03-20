#!/usr/bin/env python
"""
Initialize database from models.
Creates all tables if they don't exist.
"""
from app import create_app
from app.extensions import db
from app.models import (
    Restaurant,
    User,
    MenuItem,
    MenuCategory,
    Order,
    OrderItem,
    Payment,
    KitchenInventory,
    KitchenTransaction,
    Recipe,
    FinanceEntry,
)


def init_database():
    """Create all database tables from models."""
    app = create_app()
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✓ Database tables created successfully!")
            print()
            print("Tables created:")
            
            # List all tables
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            for table in tables:
                print(f"  - {table}")
            
            print()
            print("Next steps:")
            print("  1. Run 'python seed.py' to add sample data")
            print("  2. Run 'python run.py' to start the server")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            raise


if __name__ == "__main__":
    init_database()
