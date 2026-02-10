import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock

def test_generate_endpoint_min_ingredients(api_client):
    """Test validation rejection for <3 ingredients."""
    payload = {
        "ingredients": ["chicken", "salt"],
        "difficulty": "easy"
    }
    response = api_client.post("/generate", json=payload)
    assert response.status_code == 422
    assert "at least 3" in response.text.lower()

def test_generate_endpoint_invalid_chars(api_client):
    """Test validation rejection for invalid characters."""
    payload = {
        "ingredients": ["chicken!", "tomato", "onion"],
        "difficulty": "easy"
    }
    response = api_client.post("/generate", json=payload)
    assert response.status_code == 422
    assert "invalid characters" in response.text.lower()

def test_modify_endpoint_success(api_client, sample_recipe_data):
    """Test successful recipe modification flow (mocked)."""
    payload = {
        "original_ingredients": ["chicken", "tomato", "onion"],
        "new_ingredients": ["garlic", "basil", "oregano"],
        "difficulty": "intermediate"
    }
    
    # Mock the graph.ainvoke directly since it's already instantiated in routes.py
    with patch("src.api.routes.graph.ainvoke", new_callable=AsyncMock) as mock_invoke:
        mock_invoke.return_value = {
            "recipe": sample_recipe_data,
            "ingredients": ["chicken", "tomato", "onion", "garlic", "basil", "oregano"],
            "difficulty": "intermediate",
            "lang": "en",
            "error": None,
            "extra_ingredients": [],
            "iteration_count": 1,
            "source_node": "generate"
        }
        
        response = api_client.post("/modify", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["recipe"]["name"] == "Test Recipe"

def test_feedback_endpoint_approved(api_client, sample_recipe_data):
    """Test feedback endpoint with approved=True."""
    payload = {
        "ingredients": ["chicken", "tomato", "onion"],
        "difficulty": "easy",
        "approved": True,
        "recipe": sample_recipe_data
    }
    
    # Mock service layer to avoid real database I/O
    with patch("src.api.routes.get_recipe_service") as mock_service:
        mock_service.return_value.save_approved_recipe.return_value = 123
        response = api_client.post("/feedback", json=payload)
        assert response.status_code == 200
        assert response.json()["status"] == "success"

def test_feedback_endpoint_rejected(api_client, sample_recipe_data):
    """Test feedback endpoint with approved=False."""
    payload = {
        "ingredients": ["chicken", "tomato", "onion"],
        "difficulty": "easy",
        "approved": False,
        "recipe": sample_recipe_data
    }
    
    response = api_client.post("/feedback", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "rejected"
