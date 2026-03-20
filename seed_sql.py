#!/usr/bin/env python
"""
Load seed data from seed_data.sql into MySQL database.
Runs the SQL file directly against the database.
"""
import os
import pymysql
from dotenv import load_dotenv

load_dotenv()


def load_seed_data():
    """Execute seed_data.sql against the database."""
    
    # Get database connection from env vars
    host = os.getenv("DB_HOST", "localhost")
    port = int(os.getenv("DB_PORT", "3306"))
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    database = os.getenv("DB_NAME", "restaurant_db")
    
    sql_file = os.path.join(os.path.dirname(__file__), "seed_data.sql")
    
    if not os.path.exists(sql_file):
        print(f"✗ Error: {sql_file} not found!")
        return
    
    print(f"Loading seed data from: {sql_file}")
    print(f"Database: {database}@{host}")
    print()
    
    try:
        # Connect to database
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        
        # Read SQL file
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Execute SQL
        print("Executing SQL...")
        cursor.execute(sql_content)
        conn.commit()
        
        print("✓ Seed data loaded successfully!")
        print()
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM restaurants")
        print(f"  Restaurants: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM users")
        print(f"  Users: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM menu_items")
        print(f"  Menu Items: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM orders")
        print(f"  Orders: {cursor.fetchone()[0]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        raise


if __name__ == "__main__":
    load_seed_data()
