import pytest
import sqlite3
import json
from unittest.mock import patch, MagicMock
from src.infrastructure.database import (
    save_recipe, 
    find_recipe_by_ingredients, 
    log_error, 
    init_db
)

@pytest.fixture
def memory_db():
    import sqlite_vec
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    init_db(conn)
    yield conn
    conn.close()

def test_save_and_find_recipe(memory_db):
    """Test basic recipe CRUD."""
    ingredients = ["chicken", "tomato"]
    steps = ["cook it"]
    
    # Mock embedding service to avoid API calls
    with patch("src.infrastructure.database.get_embedding_service") as mock_service:
        mock_service.return_value.generate_embedding.return_value = [0.1] * 3072
        
        save_recipe(
            memory_db, 
            name="Chicken Tomato", 
            ingredients=ingredients, 
            difficulty="easy", 
            steps=steps
        )
        
        # Test exact match find
        recipe = find_recipe_by_ingredients(memory_db, ingredients, "easy")
        assert recipe is not None
        assert recipe["name"] == "Chicken Tomato"
        assert json.loads(recipe["ingredients"]) == ingredients
        assert json.loads(recipe["steps"]) == steps

def test_find_recipe_difficulty_mismatch(memory_db):
    """Ensure difficulty is checked in lookup."""
    with patch("src.infrastructure.database.get_embedding_service") as mock_service:
        mock_service.return_value.generate_embedding.return_value = [0.1] * 3072
        save_recipe(memory_db, "Easy One", ["water"], "easy", ["drink"])
        
        recipe = find_recipe_by_ingredients(memory_db, ["water"], "hard")
        assert recipe is None

def test_log_error(memory_db):
    """Test error logging."""
    log_error(memory_db, "TestError", "Something went wrong")
    
    cursor = memory_db.cursor()
    cursor.execute("SELECT error_type, message FROM logs")
    row = cursor.fetchone()
    assert row[0] == "TestError"
    assert row[1] == "Something went wrong"
