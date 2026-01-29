import pytest
from src.domain.ingredients import normalize_ingredient, filter_default_ingredients

def test_normalize_ingredient():
    """Test ingredient normalization."""
    assert normalize_ingredient("  CHICKEN  ") == "chicken"
    assert normalize_ingredient("TomaTo") == "tomato"
    assert normalize_ingredient("salt") == "salt"

def test_filter_default_ingredients_english():
    """Test filtering English default ingredients."""
    ingredients = ["chicken", "water", "salt", "tomato", "oil"]
    filtered = filter_default_ingredients(ingredients)
    assert filtered == ["chicken", "tomato"]

def test_filter_default_ingredients_turkish():
    """Test filtering Turkish default ingredients."""
    ingredients = ["tavuk", "su", "tuz", "domates", "yağ"]
    filtered = filter_default_ingredients(ingredients)
    assert filtered == ["tavuk", "domates"]

def test_filter_default_ingredients_preserves_order():
    """Ensure original order is preserved for non-defaults."""
    ingredients = ["pasta", "salt", "tomato", "biber", "onion"]
    filtered = filter_default_ingredients(ingredients)
    assert filtered == ["pasta", "tomato", "onion"]

def test_filter_default_ingredients_empty():
    """Test with empty list."""
    assert filter_default_ingredients([]) == []

@pytest.mark.parametrize("ingredient", [
    "water", "salt", "oil", "pepper", "cumin", "su", "tuz", "yağ", "biber", "kekik"
])
def test_all_defaults_filtered(ingredient):
    """Parameterized test for various default ingredients."""
    assert filter_default_ingredients([ingredient]) == []
