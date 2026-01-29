import pytest
from src.workflow.agents.review_agent import ReviewAgent
from src.core.exceptions import RecipeValidationError

@pytest.fixture
def agent():
    return ReviewAgent()

def test_validate_recipe_structure_success(agent):
    """Test valid structure doesn't raise."""
    recipe = {
        "name": "Test",
        "ingredients": ["item"],
        "steps": ["step"]
    }
    agent._validate_recipe_structure(recipe) # Should not raise

def test_validate_recipe_structure_missing_fields(agent):
    """Test validation failure for missing fields."""
    recipe = {"name": "Test"}
    with pytest.raises(RecipeValidationError) as exc:
        agent._validate_recipe_structure(recipe)
    assert "missing required fields" in str(exc.value)

def test_validate_recipe_structure_empty_lists(agent):
    """Test validation failure for empty lists."""
    recipe = {"name": "Test", "ingredients": [], "steps": ["step"]}
    with pytest.raises(RecipeValidationError):
        agent._validate_recipe_structure(recipe)

def test_parse_validation_response_valid(agent):
    """Test parsing a valid JSON response."""
    content = '{"valid": true, "reasoning": "Looks good", "suggested_extras": []}'
    parsed = agent._parse_validation_response(content)
    assert parsed["valid"] is True

def test_parse_validation_response_invalid(agent):
    """Test parsing an invalid JSON response with suggestions."""
    content = '{"valid": false, "reasoning": "Need salt", "suggested_extras": ["salt"]}'
    parsed = agent._parse_validation_response(content)
    assert parsed["valid"] is False
    assert "salt" in parsed["suggested_extras"]
