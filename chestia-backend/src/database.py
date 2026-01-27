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
            difficulty TEXT NOT NULL,
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

def find_recipe_by_ingredients(conn, ingredients: List[str], difficulty: str):
    """
    Find a recipe matching non-default ingredients AND difficulty level.
    
    Default ingredients (water, salt, oil, spices, etc.) are filtered out
    before lookup to optimize cache hits. Difficulty is part of cache key.
    
    This means:
    - ["pasta", "tomato", "salt"], "easy" → Different from "hard"
    - ["pasta", "tomato"], "easy" with defaults → Same cache as without defaults
    
    Args:
        conn: Database connection
        ingredients: List of ingredient names (may include defaults)
        difficulty: Recipe difficulty level ('easy', 'intermediate', 'hard')
        
    Returns:
        Recipe dict if found, None otherwise
    """
    from config import filter_default_ingredients
    
    cursor = conn.cursor()
    # Filter out default ingredients and sort for consistent lookup
    non_default_ingredients = filter_default_ingredients(ingredients)
    ingredients_json = json.dumps(sorted(non_default_ingredients))
    
    cursor.execute("""
        SELECT * FROM recipes WHERE ingredients = ? AND difficulty = ?
    """, (ingredients_json, difficulty))
    
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
