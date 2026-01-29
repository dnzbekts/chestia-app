"""
Ingredient domain logic for Chestia backend.

This module handles ingredient normalization and filtering of default/pantry ingredients.
"""

from typing import List

# Default ingredients available in every household
# Includes both English and Turkish for better user flexibility
DEFAULT_INGREDIENTS = {
    # Basic staples - English
    "water",
    "oil", "olive oil", "vegetable oil",
    "salt",
    "sugar",
    
    # Basic staples - Turkish
    "su",
    "yağ", "zeytinyağı", "sıvıyağ",
    "tuz",
    "şeker",
    
    # Common spices - English
    "pepper", "black pepper",
    "paprika", "red pepper flakes",
    "cumin",
    "cinnamon",
    "oregano",
    "basil",
    "thyme",
    "rosemary",
    "garlic powder",
    "onion powder",
    
    # Common spices - Turkish
    "biber", "karabiber",
    "kırmızıbiber", "pul biber",
    "kimyon",
    "tarçın",
    "kekik",
    "fesleğen",
    "biberiye",
    "sarımsak tozu",
    "soğan tozu",
}


def normalize_ingredient(ingredient: str) -> str:
    """
    Normalize ingredient name for comparison.
    
    Args:
        ingredient: Raw ingredient name
        
    Returns:
        Normalized ingredient name (lowercase, stripped whitespace)
    """
    return ingredient.lower().strip()


def filter_default_ingredients(ingredients: List[str]) -> List[str]:
    """
    Remove default ingredients from a list while preserving order.
    
    Args:
        ingredients: List of ingredient names
        
    Returns:
        Filtered list with only non-default ingredients, preserving original order
        
    Examples:
        >>> filter_default_ingredients(["pasta", "salt", "tomato"])
        ["pasta", "tomato"]
        
        >>> filter_default_ingredients(["CHICKEN", "Pepper", "garlic"])
        ["CHICKEN", "garlic"]
    """
    return [
        ing for ing in ingredients 
        if normalize_ingredient(ing) not in DEFAULT_INGREDIENTS
    ]
