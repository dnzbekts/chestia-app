import sqlite3
import os
import json
from typing import List, Dict, Any, Optional

def get_db_connection(db_path=None):
    if db_path is None:
        # Default to a file in the same directory
        db_path = os.path.join(os.path.dirname(__file__), 'chestia.db')
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(conn):
    cursor = conn.cursor()
    
    # Create recipes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ingredients JSON NOT NULL,
            steps JSON NOT NULL,
            metadata JSON
        )
    """)
    
    # Create logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            error_type TEXT,
            message TEXT,
            request_id TEXT
        )
    """)
    
    conn.commit()

def find_recipe_by_ingredients(conn, ingredients: List[str]):
    """Find a recipe matching the exact set of ingredients"""
    cursor = conn.cursor()
    # Normalize/Sort for consistent lookup
    ingredients_json = json.dumps(sorted(ingredients))
    
    cursor.execute("""
        SELECT * FROM recipes WHERE ingredients = ?
    """, (ingredients_json,))
    
    row = cursor.fetchone()
    if row:
        return dict(row)
    return None

def log_error(conn, error_type: str, message: str, request_id: str = None):
    """Log an error to the logs table"""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO logs (error_type, message, request_id)
        VALUES (?, ?, ?)
    """, (error_type, message, request_id))
    conn.commit()
