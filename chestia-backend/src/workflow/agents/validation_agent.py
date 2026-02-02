"""
Validation Agent - Filters non-food items and validates input parameters.
"""

from typing import List, Dict, Any
import json
import logging
from src.infrastructure.llm_factory import LLMFactory

logger = logging.getLogger(__name__)

class ValidationAgent:
    """Agent responsible for sanitizing ingredient lists and validating difficulty."""
    
    def __init__(self):
        """Initialize with structured LLM."""
        self.llm = LLMFactory.create_validation_llm() # Using search LLM for classification task

    def validate(self, ingredients: List[str], difficulty: str) -> Dict[str, Any]:
        """
        Validate ingredients and difficulty.
        
        Args:
            ingredients: List of potential ingredients
            difficulty: Requested difficulty level
            
        Returns:
            Dictionary with valid_ingredients, invalid_ingredients, normalized_difficulty, and error.
        """
        # 1. Normalize Difficulty
        valid_difficulties = ["easy", "intermediate", "hard"]
        normalized_diff = difficulty.lower().strip()
        
        if normalized_diff == "medium":
            normalized_diff = "intermediate"
        elif normalized_diff not in valid_difficulties:
            normalized_diff = "easy"
            
        # 2. Filter Ingredients using LLM
        if not ingredients:
            return {
                "valid_ingredients": [],
                "invalid_ingredients": [],
                "difficulty": normalized_diff,
                "error": "At least 3 ingredients are required."
            }

        prompt = f"""
        Role: Culinary Data Auditor
        Task: Filter a list of items to keep ONLY edible cooking ingredients.
        
        Items to classify: {', '.join(ingredients)}
        
        RULES:
        1. Keep only items that are commonly used as food, spices, or cooking liquids.
        2. Categorize items like 'glass', 'rock', 'wallet', 'phone', 'car' as INVALID.
        3. Even if slightly ambiguous, if it's not food, mark as INVALID.
        
        Return STRICT JSON format:
        {{
            "food": ["list", "of", "valid", "ingredients"],
            "invalid": ["list", "of", "unrelated", "items"]
        }}
        """
        
        try:
            response = self.llm.invoke(prompt)
            content = response.content
            
            # Simple JSON extraction
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            result = json.loads(content)
            food_items = result.get("food", [])
            invalid_items = result.get("invalid", [])
            
            logger.info(f"Validation results: {len(food_items)} food, {len(invalid_items)} invalid")
            
            if not food_items:
                return {
                    "valid_ingredients": [],
                    "invalid_ingredients": invalid_items,
                    "difficulty": normalized_diff,
                    "error": "No valid food ingredients found in the request."
                }
            
            if len(food_items) < 2:
                 return {
                    "valid_ingredients": food_items,
                    "invalid_ingredients": invalid_items,
                    "difficulty": normalized_diff,
                    "error": f"Only {len(food_items)} valid ingredients found. Minimum 2 required."
                }

            return {
                "valid_ingredients": food_items,
                "invalid_ingredients": invalid_items,
                "normalized_difficulty": normalized_diff,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Validation LLM failed: {e}")
            # Fallback: Assume all are valid if LLM fails, but log error
            return {
                "valid_ingredients": ingredients,
                "invalid_ingredients": [],
                "normalized_difficulty": normalized_diff,
                "error": None
            }
