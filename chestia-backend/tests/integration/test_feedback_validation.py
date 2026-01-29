import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_feedback_validation_malformed_recipe():
    """Verify that malformed recipe structures are rejected."""
    # Case 1: Missing name
    response = client.post("/feedback", json={
        "ingredients": ["egg"],
        "difficulty": "easy",
        "approved": True,
        "recipe": {
            "ingredients": ["egg"],
            "steps": ["cook"]
        }
    })
    assert response.status_code == 422

    # Case 2: Too long item
    response = client.post("/feedback", json={
        "ingredients": ["egg"],
        "difficulty": "easy",
        "approved": True,
        "recipe": {
            "name": "Long Recipe",
            "ingredients": ["a" * 201],
            "steps": ["cook"]
        }
    })
    assert response.status_code == 422

def test_feedback_validation_success():
    """Verify that a valid recipe is accepted."""
    response = client.post("/feedback", json={
        "ingredients": ["egg"],
        "difficulty": "easy",
        "approved": True,
        "recipe": {
            "name": "Fried Egg",
            "ingredients": ["egg", "oil"],
            "steps": ["Heat oil", "Fry egg"]
        }
    })
    assert response.status_code == 200
