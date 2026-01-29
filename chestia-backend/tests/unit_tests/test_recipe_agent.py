import pytest
import json
from src.workflow.agents.recipe_agent import RecipeAgent
from src.core.exceptions import RecipeGenerationError

@pytest.fixture
def agent():
    return RecipeAgent()

def test_sanitize_ingredients(agent):
    """Test ingredient sanitization logic."""
    raw = ["  Chicken  ", "tomato!!!", "", "a" * 100, "o'hara", "rice-cake"]
    sanitized = agent._sanitize_ingredients(raw)
    
    assert "Chicken" in sanitized
    assert "tomato" in sanitized
    assert "" not in sanitized
    assert "o'hara" not in sanitized # only alnum and " ,-" allowed
    assert "rice-cake" in sanitized
    # Long ingredients (>50) should be dropped
    assert any(len(x) >= 50 for x in raw)
    assert all(len(x) < 50 for x in sanitized)

def test_parse_json_response_success(agent):
    """Test successful JSON parsing from LLM content."""
    content = "```json\n{\"name\": \"Test\", \"ingredients\": [], \"steps\": []}\n```"
    parsed = agent._parse_json_response(content)
    assert parsed["name"] == "Test"

def test_parse_json_response_failure(agent):
    """Test parsing failure raises RecipeGenerationError."""
    content = "not a json"
    with pytest.raises(RecipeGenerationError) as exc:
        agent._parse_json_response(content)
    assert "Failed to parse recipe JSON" in str(exc.value)
