import pytest
import sys
import os
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from agents.recipe_agent import RecipeAgent, RecipeInput

@patch.dict(os.environ, {"GOOGLE_API_KEY": "test-api-key"})
def test_recipe_agent_initialization():
    """Test that RecipeAgent generates a valid recipe structure"""
    agent = RecipeAgent()
    assert agent is not None

@patch.dict(os.environ, {"GOOGLE_API_KEY": "test-api-key"})
@patch('agents.recipe_agent.ChatGoogleGenerativeAI')
def test_generate_recipe_success(mock_llm):
    """Test successful recipe generation"""
    # Mock LLM response
    mock_response = MagicMock()
    mock_response.content = '{"name": "Mock Pasta", "ingredients": ["pasta", "sauce", "cheese"], "steps": ["boil", "mix"], "metadata": {"time": "10m"}}'
    mock_llm.return_value.invoke.return_value = mock_response
    
    agent = RecipeAgent()
    ingredients = ["pasta", "sauce", "cheese"]
    
    # We mock the internal chain or llm call
    agent.llm = mock_llm.return_value
    
    result = agent.generate(ingredients, "easy")
    
    assert result["name"] == "Mock Pasta"
    assert len(result["ingredients"]) == 3
    assert "boil" in result["steps"]

@patch.dict(os.environ, {"GOOGLE_API_KEY": "test-api-key"})
def test_recipe_agent_input_validation():
    """Test that empty input raises error"""
    agent = RecipeAgent()
    with pytest.raises(ValueError):
        agent.generate([], "easy")
