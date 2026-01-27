import pytest
import sys
import os
from unittest.mock import MagicMock, patch

sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from agents.review_agent import ReviewAgent

@patch.dict(os.environ, {"GOOGLE_API_KEY": "test-api-key"})
def test_review_agent_initialization():
    agent = ReviewAgent()
    assert agent is not None

@patch.dict(os.environ, {"GOOGLE_API_KEY": "test-api-key"})

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
        "ingredients": ["pasta", "water", "salt"],
        "steps": ["Boil water", "Add pasta", "Add salt"]
    }
    ingredients = ["pasta", "water", "salt"]
    
    result = agent.validate(recipe, ingredients, "easy")
    assert result["valid"] is True

@patch.dict(os.environ, {"GOOGLE_API_KEY": "test-api-key"})
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
        "ingredients": ["steak", "salt", "pepper"],
        "steps": ["Grill steak"]
    }
    # User only provided 3 ingredients but recipe might use extra
    ingredients = ["salt", "pepper", "oil"]
    
    result = agent.validate(recipe, ingredients, "intermediate")
    assert result["valid"] is False
    assert "ingredients" in result["reasoning"].lower()

@patch.dict(os.environ, {"GOOGLE_API_KEY": "test-api-key"})
@patch('agents.review_agent.ChatGoogleGenerativeAI')
def test_validate_recipe_with_default_ingredients_allowed(mock_llm):
    """Test that recipes using default ingredients are marked as valid"""
    mock_response = MagicMock()
    mock_response.content = '{"valid": true, "reasoning": "Recipe uses default ingredients (salt, water, oil) which are allowed."}'
    mock_llm.return_value.invoke.return_value = mock_response
    
    agent = ReviewAgent()
    agent.llm = mock_llm.return_value
    
    recipe = {
        "name": "Pasta Aglio e Olio",
        "ingredients": ["pasta", "garlic", "olive oil", "salt", "pepper"],
        "steps": ["Boil pasta", "Cook garlic in oil", "Mix with pasta", "Season with salt and pepper"]
    }
    # User only provided pasta and garlic - the rest are defaults
    user_ingredients = ["pasta", "garlic", "tomato"]
    
    result = agent.validate(recipe, user_ingredients, "easy")
    assert result["valid"] is True
    assert "default" in result["reasoning"].lower()

@patch.dict(os.environ, {"GOOGLE_API_KEY": "test-api-key"})
@patch('agents.review_agent.ChatGoogleGenerativeAI')
def test_validate_recipe_with_non_default_extras_rejected(mock_llm):
    """Test that recipes using non-default extra ingredients are rejected"""
    mock_response = MagicMock()
    mock_response.content = '{"valid": false, "reasoning": "Recipe uses extra non-default ingredient: soy sauce not provided by user."}'
    mock_llm.return_value.invoke.return_value = mock_response
    
    agent = ReviewAgent()
    agent.llm = mock_llm.return_value
    
    recipe = {
        "name": "Stir Fry",
        "ingredients": ["chicken", "soy sauce", "vegetables"],
        "steps": ["Cook chicken", "Add soy sauce", "Add vegetables"]
    }
    # User provided chicken and vegetables, but NOT soy sauce (non-default)
    user_ingredients = ["chicken", "bell pepper", "onion"]
    
    result = agent.validate(recipe, user_ingredients, "medium")
    assert result["valid"] is False
    assert "soy sauce" in result["reasoning"].lower() or "extra" in result["reasoning"].lower()

@patch.dict(os.environ, {"GOOGLE_API_KEY": "test-api-key"})
@patch('agents.review_agent.ChatGoogleGenerativeAI')
def test_validate_recipe_turkish_default_ingredients(mock_llm):
    """Test that Turkish default ingredients are recognized"""
    mock_response = MagicMock()
    mock_response.content = '{"valid": true, "reasoning": "Recipe uses Turkish default ingredients (tuz, yağ) which are allowed."}'
    mock_llm.return_value.invoke.return_value = mock_response
    
    agent = ReviewAgent()
    agent.llm = mock_llm.return_value
    
    recipe = {
        "name": "Menemen",
        "ingredients": ["domates", "yumurta", "tuz", "yağ", "biber"],
        "steps": ["Kavur domates", "Ekle yumurta", "Tuz ile tatlandir"]
    }
    # User provided tomatoes and eggs, spices/oil/salt are default
    user_ingredients = ["domates", "yumurta", "sivribiber"]
    
    result = agent.validate(recipe, user_ingredients, "easy")
    assert result["valid"] is True
