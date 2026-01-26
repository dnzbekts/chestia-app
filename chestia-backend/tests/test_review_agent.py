import pytest
import sys
import os
from unittest.mock import MagicMock, patch

sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from agents.review_agent import ReviewAgent

def test_review_agent_initialization():
    agent = ReviewAgent()
    assert agent is not None

@patch('agents.review_agent.ChatGoogleGenerativeAI')
def test_validate_recipe_success(mock_llm):
    """Test successful validation"""
    mock_response = MagicMock()
    # Expecting the agent to return a JSON with valid: true/false and reasoning
    mock_response.content = '{"valid": true, "reasoning": "Recipe is consistent."}'
    mock_llm.return_value.invoke.return_value = mock_response
    
    agent = ReviewAgent()
    agent.llm = mock_llm.return_value
    
    recipe = {
        "name": "Pasta",
        "ingredients": ["pasta", "water"],
        "steps": ["Boil water", "Add pasta"]
    }
    ingredients = ["pasta", "water"]
    
    result = agent.validate(recipe, ingredients)
    assert result["valid"] is True

@patch('agents.review_agent.ChatGoogleGenerativeAI')
def test_validate_recipe_hallucination(mock_llm):
    """Test catching a hallucination (missing ingredients or illogical steps)"""
    mock_response = MagicMock()
    mock_response.content = '{"valid": false, "reasoning": "Recipe uses ingredients not provided."}'
    mock_llm.return_value.invoke.return_value = mock_response
    
    agent = ReviewAgent()
    agent.llm = mock_llm.return_value
    
    recipe = {
        "name": "Steak",
        "ingredients": ["steak", "salt"],
        "steps": ["Grill steak"]
    }
    # User only provided 'salt'
    ingredients = ["salt"]
    
    result = agent.validate(recipe, ingredients)
    assert result["valid"] is False
    assert "ingredients" in result["reasoning"].lower()
