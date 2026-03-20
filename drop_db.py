#!/usr/bin/env python
"""
Drop all database tables.
WARNING: This will delete all data permanently!
"""
import sys
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


def drop_all_tables():
    """Drop all database tables."""
    app = create_app()
    
    with app.app_context():
        try:
            # Get confirmation
            print("⚠️  WARNING: This will delete ALL data permanently!")
            print()
            print("Tables to be dropped:")
            
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if not tables:
                print("  (no tables found)")
                return
            
            for table in tables:
                print(f"  - {table}")
            
            print()
            response = input("Are you sure you want to continue? Type 'YES' to confirm: ")
            
            if response.strip() != 'YES':
                print("❌ Cancelled.")
                return
            
            # Disable foreign key checks for MySQL
            with db.engine.connect() as conn:
                conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
                conn.commit()
            
            # Drop all tables
            db.drop_all()
            
            # Re-enable foreign key checks
            with db.engine.connect() as conn:
                conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
                conn.commit()
            
            print()
            print("✓ All tables dropped successfully!")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            raise


if __name__ == "__main__":
    drop_all_tables()
