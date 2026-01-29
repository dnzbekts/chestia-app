import pytest
from pydantic import ValidationError
from src.api.schemas import GenerateRequest, ModifyRequest, RecipeSchema, FeedbackRequest

def test_generate_request_valid():
    """Test valid GenerateRequest."""
    payload = {
        "ingredients": ["chicken", "tomato", "onion"],
        "difficulty": "easy",
        "lang": "en"
    }
    req = GenerateRequest(**payload)
    assert req.ingredients == payload["ingredients"]
    assert req.difficulty == payload["difficulty"]

def test_generate_request_invalid_chars():
    """Test GenerateRequest with invalid characters in ingredients."""
    with pytest.raises(ValidationError) as exc:
        GenerateRequest(
            ingredients=["chicken!", "tomato"],
            difficulty="easy"
        )
    assert "Ingredient contains invalid characters" in str(exc.value)

def test_generate_request_too_few_ingredients():
    """Test GenerateRequest with less than 3 ingredients."""
    with pytest.raises(ValidationError):
        GenerateRequest(
            ingredients=["chicken", "tomato"],
            difficulty="easy"
        )

def test_generate_request_too_many_ingredients():
    """Test GenerateRequest with more than 20 ingredients."""
    with pytest.raises(ValidationError):
        GenerateRequest(
            ingredients=["ing"] * 21,
            difficulty="easy"
        )

def test_modify_request_valid():
    """Test valid ModifyRequest."""
    payload = {
        "original_ingredients": ["chicken", "tomato", "onion"],
        "new_ingredients": ["garlic"],
        "difficulty": "intermediate",
        "lang": "tr"
    }
    req = ModifyRequest(**payload)
    assert req.original_ingredients == payload["original_ingredients"]
    assert req.new_ingredients == payload["new_ingredients"]

def test_recipe_schema_max_content():
    """Test RecipeSchema content length limits."""
    # Each ingredient/step has 200 char limit in validator
    with pytest.raises(ValidationError) as exc:
        RecipeSchema(
            name="Long Recipe",
            ingredients=["a" * 201],
            steps=["cook"]
        )
    assert "Item content too long" in str(exc.value)

def test_feedback_request_valid(sample_recipe_data):
    """Test valid FeedbackRequest."""
    payload = {
        "ingredients": ["chicken"],
        "difficulty": "easy",
        "approved": True,
        "recipe": sample_recipe_data
    }
    req = FeedbackRequest(**payload)
    assert req.approved is True
    assert req.recipe.name == "Test Recipe"
