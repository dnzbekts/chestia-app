import pytest
import sys
import os
import sqlite3
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.infrastructure.database import init_db, get_db_connection, find_recipe_by_ingredients

DB_PATH = ":memory:"

def test_difficulty_separates_cache():
    """Test that same ingredients + different difficulty = different cache entries"""
    with get_db_connection(DB_PATH) as conn:
        init_db(conn)
        
        ingredients = ["pasta", "tomato"]
        ingredients_json = json.dumps(sorted(ingredients))
        
        cursor = conn.cursor()
        
        # Save easy recipe
        cursor.execute("""
            INSERT INTO recipes (name, ingredients, difficulty, steps, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, ("Easy Pasta", ingredients_json, "easy", json.dumps(["Boil", "Mix"]), '{}'))
        
        # Save hard recipe (same ingredients, different difficulty)
        cursor.execute("""
            INSERT INTO recipes (name, ingredients, difficulty, steps, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, ("Complex Pasta", ingredients_json, "hard", json.dumps(["Prepare sauce", "Cook al dente", "Plate elegantly"]), '{}'))
        
        # Save intermediate recipe
        cursor.execute("""
            INSERT INTO recipes (name, ingredients, difficulty, steps, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, ("Medium Pasta", ingredients_json, "intermediate", json.dumps(["Cook pasta", "Make sauce", "Combine"]), '{}'))
        
        conn.commit()
        
        # Query for easy - should get Easy Pasta
        easy_recipe = find_recipe_by_ingredients(conn, ["pasta", "tomato", "salt"], "easy")
        assert easy_recipe is not None
        assert easy_recipe["name"] == "Easy Pasta"
        
        # Query for hard - should get Complex Pasta
        hard_recipe = find_recipe_by_ingredients(conn, ["pasta", "tomato", "water"], "hard")
        assert hard_recipe is not None
        assert hard_recipe["name"] == "Complex Pasta"
        
        # Query for intermediate - should get Medium Pasta
        medium_recipe = find_recipe_by_ingredients(conn, ["pasta", "tomato", "oil"], "intermediate")
        assert medium_recipe is not None
        assert medium_recipe["name"] == "Medium Pasta"
        
        # Verify they are actually different recipes
        assert easy_recipe["name"] != hard_recipe["name"]
        assert easy_recipe["name"] != medium_recipe["name"]
