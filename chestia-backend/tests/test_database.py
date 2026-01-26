import pytest
import sys
import os
import sqlite3

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from database import init_db, get_db_connection

DB_PATH = ":memory:"

def test_database_connection():
    """Test that we can connect to the database"""
    conn = get_db_connection(DB_PATH)
    assert isinstance(conn, sqlite3.Connection)
    conn.close()

def test_init_db():
    """Test that tables are created correctly"""
    conn = get_db_connection(DB_PATH)
    init_db(conn)
    
    cursor = conn.cursor()
    
    # Check recipes table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='recipes'")
    assert cursor.fetchone() is not None
    
    # Check logs table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='logs'")
    assert cursor.fetchone() is not None
    
    conn.close()

def test_insert_and_retrieve_recipe():
    """Test inserting and retrieving a recipe"""
    conn = get_db_connection(DB_PATH)
    init_db(conn)
    cursor = conn.cursor()
    
    recipe_data = {
        "name": "Test Pasta",
        "ingredients": '["pasta", "tomato"]',
        "steps": '["Boil water", "Cook pasta"]',
        "metadata": '{"time": "20min", "difficulty": "easy"}'
    }
    
    cursor.execute("""
        INSERT INTO recipes (name, ingredients, steps, metadata)
        VALUES (:name, :ingredients, :steps, :metadata)
    """, recipe_data)
    conn.commit()
    
    cursor.execute("SELECT * FROM recipes WHERE name='Test Pasta'")
    row = cursor.fetchone()
    
    assert row is not None
    assert row[1] == "Test Pasta"
    assert "pasta" in row[2]
    
    conn.close()

def test_find_recipe_by_ingredients():
    """Test finding a recipe by sorted ingredients match"""
    import json
    from database import find_recipe_by_ingredients
    
    conn = get_db_connection(DB_PATH)
    init_db(conn)
    
    ingredients = ["egg", "tomato"]
    # We expect the DB to store sorted JSON strings
    ingredients_json = json.dumps(sorted(ingredients))
    
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO recipes (name, ingredients, steps, metadata)
        VALUES (?, ?, ?, ?)
    """, ("Menemen", ingredients_json, '["Cook tomato", "Add egg"]', '{}'))
    conn.commit()
    
    # Test perfect match (order shouldn't matter for input as we sort in the function)
    found = find_recipe_by_ingredients(conn, ["tomato", "egg"])
    assert found is not None
    assert found["name"] == "Menemen"
    
    # Test mismatch
    not_found = find_recipe_by_ingredients(conn, ["tomato", "onion"])
    assert not_found is None
    
    conn.close()
