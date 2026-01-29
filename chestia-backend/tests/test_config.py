import pytest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.domain.ingredients import (
    DEFAULT_INGREDIENTS,
    normalize_ingredient,
    filter_default_ingredients
)

def test_default_ingredients_set_exists():
    """Test that DEFAULT_INGREDIENTS constant is defined and is a set"""
    assert DEFAULT_INGREDIENTS is not None
    assert isinstance(DEFAULT_INGREDIENTS, set)
    assert len(DEFAULT_INGREDIENTS) > 0

def test_normalize_ingredient_lowercase():
    """Test ingredient normalization converts to lowercase"""
    assert normalize_ingredient("SALT") == "salt"
    assert normalize_ingredient("Salt") == "salt"
    assert normalize_ingredient("sAlT") == "salt"

def test_normalize_ingredient_strips_whitespace():
    """Test ingredient normalization removes leading/trailing whitespace"""
    assert normalize_ingredient("  salt  ") == "salt"
    assert normalize_ingredient("\tsalt\n") == "salt"
    assert normalize_ingredient(" water ") == "water"

def test_normalize_ingredient_preserves_internal_spaces():
    """Test that internal spaces are preserved"""
    assert normalize_ingredient("olive oil") == "olive oil"
    assert normalize_ingredient("black pepper") == "black pepper"

def test_filter_default_ingredients_removes_basic_staples():
    """Test that basic staples are filtered out"""
    ingredients = ["pasta", "salt", "water", "cheese"]
    filtered = filter_default_ingredients(ingredients)
    
    assert "pasta" in filtered
    assert "cheese" in filtered
    assert "salt" not in filtered
    assert "water" not in filtered

def test_filter_default_ingredients_removes_spices():
    """Test that common spices are filtered out"""
    ingredients = ["chicken", "pepper", "paprika", "cumin"]
    filtered = filter_default_ingredients(ingredients)
    
    assert "chicken" in filtered
    assert "pepper" not in filtered
    assert "paprika" not in filtered
    assert "cumin" not in filtered

def test_filter_default_ingredients_case_insensitive():
    """Test that filtering is case-insensitive"""
    ingredients = ["PASTA", "SALT", "Pepper", "cheese"]
    filtered = filter_default_ingredients(ingredients)
    
    assert len(filtered) == 2  # Only pasta and cheese remain
    # Normalize for comparison
    filtered_normalized = [normalize_ingredient(i) for i in filtered]
    assert "pasta" in filtered_normalized
    assert "cheese" in filtered_normalized

def test_filter_default_ingredients_turkish_support():
    """Test that Turkish ingredient names are recognized"""
    ingredients = ["makarna", "tuz", "su", "peynir"]
    filtered = filter_default_ingredients(ingredients)
    
    assert "makarna" in filtered  # pasta
    assert "peynir" in filtered   # cheese
    assert "tuz" not in filtered  # salt
    assert "su" not in filtered   # water

def test_filter_default_ingredients_empty_list():
    """Test that empty list returns empty list"""
    ingredients = []
    filtered = filter_default_ingredients(ingredients)
    
    assert filtered == []

def test_filter_default_ingredients_all_default():
    """Test with list containing only default ingredients"""
    ingredients = ["salt", "water", "oil", "sugar"]
    filtered = filter_default_ingredients(ingredients)
    
    assert filtered == []

def test_filter_default_ingredients_preserves_order():
    """Test that filtering preserves original order"""
    ingredients = ["tomato", "salt", "pasta", "water", "cheese"]
    filtered = filter_default_ingredients(ingredients)
    
    # Should maintain: tomato, pasta, cheese order
    assert filtered == ["tomato", "pasta", "cheese"]

def test_default_ingredients_contains_expected_items():
    """Test that DEFAULT_INGREDIENTS includes all required items"""
    # Basic staples
    assert "water" in DEFAULT_INGREDIENTS
    assert "su" in DEFAULT_INGREDIENTS  # Turkish
    assert "salt" in DEFAULT_INGREDIENTS
    assert "tuz" in DEFAULT_INGREDIENTS  # Turkish
    assert "oil" in DEFAULT_INGREDIENTS
    assert "yağ" in DEFAULT_INGREDIENTS  # Turkish
    assert "sugar" in DEFAULT_INGREDIENTS
    assert "şeker" in DEFAULT_INGREDIENTS  # Turkish
    
    # Common spices
    assert "pepper" in DEFAULT_INGREDIENTS
    assert "paprika" in DEFAULT_INGREDIENTS
    assert "cumin" in DEFAULT_INGREDIENTS
    assert "cinnamon" in DEFAULT_INGREDIENTS
