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
    """Test inserting and retrieving a recipe with difficulty"""
    conn = get_db_connection(DB_PATH)
    init_db(conn)
    cursor = conn.cursor()
    
    recipe_data = {
        "name": "Test Pasta",
        "ingredients": '["pasta", "tomato", "garlic"]',
        "difficulty": "easy",
        "steps": '["Boil water", "Cook pasta", "Add sauce"]',
        "metadata": '{"time": "20min"}'
    }
    
    cursor.execute("""
        INSERT INTO recipes (name, ingredients, difficulty, steps, metadata)
        VALUES (:name, :ingredients, :difficulty, :steps, :metadata)
    """, recipe_data)
    conn.commit()
    
    cursor.execute("SELECT * FROM recipes WHERE name='Test Pasta'")
    row = cursor.fetchone()
    
    assert row is not None
    assert row[1] == "Test Pasta"
    assert "pasta" in row[2]
    assert row[3] == "easy"  # difficulty column
    
    conn.close()

def test_find_recipe_by_ingredients():
    """Test finding a recipe by sorted ingredients match"""
    import json
    from database import find_recipe_by_ingredients
    
    conn = get_db_connection(DB_PATH)
    init_db(conn)
    
    ingredients = ["egg", "tomato", "onion"]
    # We expect the DB to store sorted JSON strings
    ingredients_json = json.dumps(sorted(ingredients))
    
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO recipes (name, ingredients, difficulty, steps, metadata)
        VALUES (?, ?, ?, ?, ?)
    """, ("Menemen", ingredients_json, "intermediate", '["Cook tomato", "Cook onion", "Add egg"]', '{}'))
    conn.commit()
    
    # Test perfect match (order shouldn't matter for input as we sort in the function)
    found = find_recipe_by_ingredients(conn, ["tomato", "egg", "onion"], "intermediate")
    assert found is not None
    assert found["name"] == "Menemen"
    
    # Test mismatch
    not_found = find_recipe_by_ingredients(conn, ["tomato", "onion", "pepper"], "intermediate")
    assert not_found is None
    
    conn.close()

def test_find_recipe_ignores_default_ingredients():
    """Test that cache lookup ignores default ingredients"""
    import json
    from database import find_recipe_by_ingredients
    
    conn = get_db_connection(DB_PATH)
    init_db(conn)
    
    # Store a recipe with only non-default ingredients
    non_default_ingredients = ["pasta", "tomato", "cheese"]
    ingredients_json = json.dumps(sorted(non_default_ingredients))
    
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO recipes (name, ingredients, difficulty, steps, metadata)
        VALUES (?, ?, ?, ?, ?)
    """, ("Pasta", ingredients_json, "easy", '["Cook pasta", "Add sauce"]', '{}'))
    conn.commit()
    
    # Query WITH default ingredients - should still match
    found = find_recipe_by_ingredients(conn, ["pasta", "tomato", "cheese", "salt", "olive oil", "water"], "easy")
    assert found is not None
    assert found["name"] == "Pasta"
    
    # Query WITHOUT any defaults - should also match
    found2 = find_recipe_by_ingredients(conn, ["pasta", "tomato", "cheese"], "easy")
    assert found2 is not None
    assert found2["name"] == "Pasta"
    
    conn.close()

def test_find_recipe_default_ingredients_not_differentiating():
    """Test that ['pasta', 'salt'] and ['pasta', 'pepper'] both match ['pasta']"""
    import json
    from database import find_recipe_by_ingredients
    
    conn = get_db_connection(DB_PATH)
    init_db(conn)
    
    # Store recipe with just 'pasta' (non-default)
    ingredients_json = json.dumps(["pasta"])
    
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO recipes (name, ingredients, difficulty, steps, metadata)
        VALUES (?, ?, ?, ?, ?)
    """, ("Simple Pasta", ingredients_json, "easy", '["Cook pasta"]', '{}'))
    conn.commit()
    
    # Both queries should match the same cached recipe
    found1 = find_recipe_by_ingredients(conn, ["pasta", "salt", "water"], "easy")
    found2 = find_recipe_by_ingredients(conn, ["pasta", "pepper", "oil"], "easy")
    
    assert found1 is not None
    assert found2 is not None
    assert found1["name"] == "Simple Pasta"
    assert found2["name"] == "Simple Pasta"
    
    conn.close()
