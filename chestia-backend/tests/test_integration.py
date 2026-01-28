import pytest
from fastapi.testclient import TestClient
import sys
import os
from unittest.mock import patch, MagicMock

# Add src to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from api import app
from utils import i18n

client = TestClient(app)

@pytest.fixture
def mock_db_connection():
    with patch('api.get_db_connection') as mock_conn:
        yield mock_conn

@pytest.fixture
def mock_graph_invoke():
    with patch('api.graph.invoke') as mock_invoke:
        yield mock_invoke

def test_generate_cache_hit(mock_db_connection):
    """Scenario 2.1: Verify cache hit returns recipe instantly."""
    with patch('api.graph.invoke') as mock_invoke:
        mock_recipe = {
            "name": "Cached Pasta",
            "ingredients": ["pasta", "tomato"],
            "steps": ["Step 1"],
            "metadata": {"difficulty": "easy"}
        }
        mock_invoke.return_value = {
            "recipe": mock_recipe,
            "iteration_count": 1,
            "error": None
        }
        
        response = client.post("/generate", json={
            "ingredients": ["pasta", "tomato", "salt"],
            "difficulty": "easy",
            "lang": "en"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["recipe"]["name"] == "Cached Pasta"

def test_generate_llm_success_tr():
    """Scenario 2.2: Verify successful generation with Turkish language."""
    with patch('api.graph.invoke') as mock_invoke:
        mock_recipe = {
            "name": "Domatesli Makarna",
            "ingredients": ["makarna", "domates"],
            "steps": ["Pişir"],
            "metadata": {"difficulty": "easy"}
        }
        mock_invoke.return_value = {
            "recipe": mock_recipe,
            "iteration_count": 1,
            "extra_ingredients": [],
            "error": None
        }
        
        response = client.post("/generate", json={
            "ingredients": ["makarna", "domates", "su"],
            "difficulty": "easy",
            "lang": "tr"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["recipe"]["name"] == "Domatesli Makarna"

def test_generate_auto_retry_success():
    """Scenario 2.3: Verify auto-retry loop when extra ingredients are needed."""
    with patch('api.graph.invoke') as mock_invoke:
        mock_recipe = {
            "name": "Retried Recipe",
            "ingredients": ["egg", "milk"],
            "steps": ["Step 1"],
            "metadata": {"difficulty": "easy"}
        }
        # In reality, the graph is invoked once from the API.
        # The auto-retry happens INSIDE the graph.
        # So we just mock the final state returned by the graph.
        mock_invoke.return_value = {
            "recipe": mock_recipe,
            "iteration_count": 2,
            "extra_ingredients": ["milk"],
            "error": None
        }
        
        response = client.post("/generate", json={
            "ingredients": ["egg", "oil", "salt"],
            "difficulty": "easy",
            "lang": "en"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["extra_ingredients_added"] == ["milk"]
        assert data["iterations"] == 2

def test_generate_failure_max_iterations_en():
    """Scenario 2.4: Verify English error after max iterations fail."""
    with patch('api.graph.invoke') as mock_invoke:
        expected_error = i18n.get_message(i18n.RECIPE_NOT_FOUND, "en")
        mock_invoke.return_value = {
            "recipe": None,
            "iteration_count": 3,
            "extra_ingredients": ["garlic", "onion"],
            "error": expected_error
        }
        
        response = client.post("/generate", json={
            "ingredients": ["stone", "water", "salt"],
            "difficulty": "hard",
            "lang": "en"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert data["message"] == expected_error

def test_validation_failure_default_only_tr():
    """Scenario 2.5: Verify rejection of only-default ingredients in Turkish."""
    response = client.post("/generate", json={
        "ingredients": ["su", "tuz", "yağ"],
        "difficulty": "easy",
        "lang": "tr"
    })
    
    assert response.status_code == 422
    data = response.json()
    expected_error = i18n.get_message(i18n.MIN_INGREDIENTS, "tr")
    assert data["detail"] == expected_error

def test_modify_recipe_success():
    """Scenario 2.6: Verify modification flow."""
    with patch('api.graph.invoke') as mock_invoke:
        mock_recipe = {"name": "Modified Pasta", "ingredients": ["pasta", "cream", "cheese"]}
        mock_invoke.return_value = {
            "recipe": mock_recipe,
            "extra_ingredients": [],
            "error": None
        }
        
        response = client.post("/modify", json={
            "original_ingredients": ["pasta", "tomato", "onion"],
            "new_ingredients": ["cream"],
            "difficulty": "hard",
            "modification_note": "make it creamy",
            "lang": "en"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["recipe"]["name"] == "Modified Pasta"

def test_feedback_success_en():
    """Scenario 2.7: Verify feedback successfully saves."""
    # We need to mock generate_embedding because save_recipe calls it
    with patch('database.generate_embedding') as mock_embed:
        mock_embed.return_value = [0.1] * 768
        
        with patch('api.get_db_connection') as mock_conn:
            mock_cursor = MagicMock()
            mock_conn.return_value.cursor.return_value = mock_cursor
            
            response = client.post("/feedback", json={
                "ingredients": ["pasta", "tomato", "cheese"],
                "difficulty": "easy",
                "approved": True,
                "recipe": {"name": "Best Pasta", "steps": ["step"]},
                "lang": "en"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["message"] == i18n.get_message(i18n.FEEDBACK_SUCCESS, "en")
            # Should be called twice: once for recipes, once for vec_recipes
            assert mock_cursor.execute.call_count >= 2

def test_min_ingredients_validation_en():
    """Test that < 3 ingredients returns 422 error."""
    response = client.post("/generate", json={
        "ingredients": ["pasta", "salt"],
        "difficulty": "easy",
        "lang": "en"
    })
    
    assert response.status_code == 422
    data = response.json()
    # Pydantic validation error format
    assert "detail" in data

def test_max_ingredients_validation_en():
    """Test that > 20 ingredients returns 422 error."""
    too_many_ingredients = [f"ingredient{i}" for i in range(21)]
    
    response = client.post("/generate", json={
        "ingredients": too_many_ingredients,
        "difficulty": "easy",
        "lang": "en"
    })
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data

def test_modify_min_ingredients_validation():
    """Test that /modify with < 3 original_ingredients returns 422."""
    response = client.post("/modify", json={
        "original_ingredients": ["pasta", "salt"],
        "difficulty": "easy",
        "lang": "en"
    })
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
