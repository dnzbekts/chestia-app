import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

"""
COMPREHENSIVE LIVE SCENARIO TESTS
---------------------------------
This file contains realistic test scenarios for the Chestia Backend.
It covers happy paths, edge cases, and failure modes across all endpoints.

NOTE TO USER:
By default, the project's `conftest.py` mocks the LLM and Tavily API keys to prevent accidental cost usage.
If you wish to run these tests with REAL live calls to Google Gemini and Tavily:
1. Ensure your `.env` file has valid `GOOGLE_API_KEY` and `TAVILY_API_KEY`.
2. You must temporarily disable the `mock_api_keys` fixture in `tests/conftest.py` (e.g., by commenting it out or changing `autouse=True` to `False`).
3. Run specifically this file: `pytest tests/test_live_scenarios.py -v`

If you run this without disabling the mocks, it will simulate the scenarios using the mocked LLM logic defined in the codebase.
"""

class TestLiveScenarios:

    # ----------------------------------------------------------------
    # 1. GENERATE ENDPOINT SCENARIOS
    # ----------------------------------------------------------------

    def test_generate_happy_path_en(self):
        """Standard successful generation in English with typical ingredients."""
        payload = {
            "ingredients": ["chicken breast", "rice", "bell pepper"],
            "difficulty": "easy",
            "lang": "en"
        }
        response = client.post("/generate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "recipe" in data
        assert data["recipe"]["name"] is not None
        assert len(data["recipe"]["steps"]) > 0

    def test_generate_happy_path_tr(self):
        """Standard successful generation in Turkish."""
        payload = {
            "ingredients": ["kıyma", "domates", "soğan"],
            "difficulty": "intermediate",
            "lang": "tr"
        }
        response = client.post("/generate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        # Since logic might mock responses, we mostly check structure here
        assert "recipe" in data

    def test_generate_edge_case_min_ingredients(self):
        """Test with exactly 3 non-default ingredients (minimum allowed)."""
        payload = {
            "ingredients": ["egg", "flour", "milk"],
            "difficulty": "easy",
            "lang": "en"
        }
        response = client.post("/generate", json=payload)
        assert response.status_code == 200

    def test_generate_edge_case_max_ingredients(self):
        """Test with exactly 20 ingredients (maximum allowed)."""
        ingredients = [f"ingredient {i}" for i in range(20)]
        payload = {
            "ingredients": ingredients,
            "difficulty": "hard",
            "lang": "en"
        }
        response = client.post("/generate", json=payload)
        assert response.status_code == 200  # Should be accepted, graph handles logic

    def test_generate_edge_case_exotic_ingredients(self):
        """Test with rare or exotic ingredients to check LLM handling."""
        payload = {
            "ingredients": ["dragon fruit", "durian", "goji berries"],
            "difficulty": "hard",
            "lang": "en"
        }
        response = client.post("/generate", json=payload)
        assert response.status_code == 200

    def test_generate_failure_insufficient_ingredients_count(self):
        """Fail when < 3 ingredients are provided."""
        payload = {
            "ingredients": ["chicken", "rice"],
            "difficulty": "easy",
            "lang": "en"
        }
        response = client.post("/generate", json=payload)
        assert response.status_code == 422
        # Pydantic validation error

    def test_generate_failure_only_default_ingredients(self):
        """Fail when 3 ingredients are provided but they are all default pantry items (filtered out)."""
        # Assuming 'salt', 'water', 'oil' are in the default list
        payload = {
            "ingredients": ["salt", "water", "oil"],
            "difficulty": "easy",
            "lang": "en"
        }
        response = client.post("/generate", json=payload)
        # Should fail validation because filtered list is empty
        assert response.status_code == 422
        # Verify custom error for min ingredients
        assert "at least" in response.json()["detail"].lower()

    def test_generate_failure_sanitization(self):
        """Fail when ingredients contain invalid characters."""
        payload = {
            "ingredients": ["chicken", "rice", "onion$"],
            "difficulty": "easy",
            "lang": "en"
        }
        response = client.post("/generate", json=payload)
        assert response.status_code == 422
        assert "ingredient contains invalid characters" in response.text.lower()

    def test_generate_failure_too_long_ingredient(self):
        """Fail when an ingredient name is absurdly long."""
        long_name = "a" * 51
        payload = {
            "ingredients": ["chicken", "rice", long_name],
            "difficulty": "easy",
            "lang": "en"
        }
        response = client.post("/generate", json=payload)
        assert response.status_code == 422

    # ----------------------------------------------------------------
    # 2. MODIFY ENDPOINT SCENARIOS
    # ----------------------------------------------------------------

    def test_modify_add_valid_ingredient(self):
        """Modify request adding a valid new ingredient."""
        payload = {
            "original_ingredients": ["pasta", "tomato", "basil"],
            "new_ingredients": ["cheese"],
            "difficulty": "easy",
            "modification_note": "Add cheese on top",
            "lang": "en"
        }
        response = client.post("/modify", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_modify_change_difficulty_only(self):
        """Modify request changing only difficulty."""
        payload = {
            "original_ingredients": ["steak", "potato", "asparagus"],
            "new_ingredients": [],
            "difficulty": "hard",  # Changed to hard
            "modification_note": "Make it gourmet",
            "lang": "en"
        }
        response = client.post("/modify", json=payload)
        assert response.status_code == 200

    def test_modify_failure_empty_total_ingredients(self):
        """Modify request resulting in empty ingredients list."""
        # This is strictly validated at Pydantic level (min_length=3 on original)
        payload = {
            "original_ingredients": ["salt", "pepper"], # Less than 3
            "new_ingredients": [],
            "difficulty": "easy",
            "lang": "en"
        }
        response = client.post("/modify", json=payload)
        assert response.status_code == 422

    # ----------------------------------------------------------------
    # 3. FEEDBACK ENDPOINT SCENARIOS
    # ----------------------------------------------------------------

    def test_feedback_approval_flow(self):
        """Test approving and saving a valid recipe."""
        # First generate or create a dummy recipe object
        mock_recipe = {
            "name": "Test Recipe",
            "ingredients": ["a", "b", "c"],
            "steps": ["step 1"],
            "metadata": {}
        }
        
        payload = {
            "ingredients": ["a", "b", "c"],
            "difficulty": "easy",
            "approved": True,
            "recipe": mock_recipe,
            "lang": "en"
        }
        response = client.post("/feedback", json=payload)
        assert response.status_code == 200
        assert response.json()["status"] == "success"

    def test_feedback_rejection_flow(self):
        """Test rejecting a recipe (should not save to DB)."""
        mock_recipe = {"name": "Bad Recipe", "ingredients": [], "steps": [], "metadata": {}}
        payload = {
            "ingredients": ["a", "b", "c"],
            "difficulty": "easy",
            "approved": False,
            "recipe": mock_recipe,
            "lang": "en"
        }
        response = client.post("/feedback", json=payload)
        assert response.status_code == 200
        assert response.json()["status"] == "rejected"
