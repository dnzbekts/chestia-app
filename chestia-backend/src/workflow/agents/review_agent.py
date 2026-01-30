"""
Review Agent - Validates generated recipes for accuracy and quality.

Refactored to use LLMFactory and follow DRY/SOLID principles.
"""

from typing import List, Dict, Any
import json
from src.infrastructure.llm_factory import LLMFactory
from src.core.exceptions import RecipeValidationError
import logging


logger = logging.getLogger(__name__)

class ReviewAgent:
    """Agent responsible for validating recipe quality and accuracy."""
    
    def __init__(self):
        """Initialize the ReviewAgent with configured LLM."""
        self.llm = LLMFactory.create_review_llm()

    def _validate_recipe_structure(self, recipe: Dict[str, Any]) -> None:
        """
        Validate that recipe has required structure.
        
        Args:
            recipe: Recipe dictionary to validate
            
        Raises:
            RecipeValidationError: If recipe structure is invalid
        """
        required_fields = ["name", "ingredients", "steps"]
        missing_fields = [field for field in required_fields if field not in recipe]
        
        if missing_fields:
            raise RecipeValidationError(
                f"Recipe missing required fields: {', '.join(missing_fields)}",
                details={"recipe": recipe}
            )
        
        if not recipe["ingredients"]:
            raise RecipeValidationError(
                "Recipe must have at least one ingredient",
                details={"ingredients": recipe.get("ingredients")}
            )
        
        if not recipe["steps"]:
            raise RecipeValidationError(
                "Recipe must have at least one step",
                details={"steps": recipe.get("steps")}
            )

    def _parse_validation_response(self, content: str) -> Dict[str, Any]:
        """
        Parse validation response from LLM.
        
        Args:
            content: Raw LLM response
            
        Returns:
            Parsed validation result
        """
        try:
            cleaned = content.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Return conservative default on parse failure
            return {
                "valid": False,
                "reasoning": "Reviewer failed to provide a valid JSON response.",
                "suggested_extras": []
            }

    def validate(
        self, 
        recipe: Dict[str, Any], 
        user_ingredients: List[str], 
        difficulty: str,
        source: str = "generate"
    ) -> Dict[str, Any]:
        """
        Validate recipe for hallucinations, logic errors, and difficulty match.
        
        Args:
            recipe: Generated recipe to validate
            user_ingredients: Original user-provided ingredients
            difficulty: Requested difficulty level
            source: Recipe source - 'generate', 'web_search', 'cache', 'semantic_search'
            
        Returns:
            Validation result with 'valid', 'reasoning', and 'suggested_extras' keys
            
        Raises:
            RecipeValidationError: If recipe structure is invalid
        """
        from src.domain.ingredients import DEFAULT_INGREDIENTS
        
        # Validate structure before processing
        self._validate_recipe_structure(recipe)
        
        # Format default ingredients list for prompt
        default_ingredients_list = ', '.join(sorted(DEFAULT_INGREDIENTS))
        
        # Use relaxed rules for web_search sources
        if source == "web_search":
            validation_rules = f"""
        VALIDATION RULES (Relaxed for Web Search):
        1. Recipe ingredients should have 80%+ overlap with User Ingredients
        2. Recipe MAY include 1-2 more additional common cooking ingredients
        3. Recipe MAY use any DEFAULT ingredients freely
        4. Steps must be logical and achievable
        5. Must be a real, edible recipe
        6. Complexity should reasonably match {difficulty}
        """
        else:
            validation_rules = f"""
        VALIDATION RULES (Strict for Generated):
        1. Recipe MAY use any DEFAULT ingredients freely
        2. Recipe MUST primarily use User Ingredients
        3. If recipe uses NON-DEFAULT ingredients NOT in user list -> INVALID
        4. Steps must be logical and achievable
        5. Must be a real, edible recipe
        6. Complexity must match {difficulty}:
           - Easy: Simple steps, minimal technique
           - Intermediate: Moderate complexity
           - Hard: Advanced techniques
        """
        
        prompt = f"""
        Role: Senior Culinary Reviewer
        Task: Validate recipe and suggest improvements if invalid.
        
        Source: {source}
        User Ingredients: {', '.join(user_ingredients)}
        Requested Difficulty: {difficulty}
        
        DEFAULT INGREDIENTS (always available, don't count as extras):
        {default_ingredients_list}
        
        Generated Recipe:
        Name: {recipe.get('name')}
        Ingredients: {', '.join(recipe.get('ingredients', []))}
        Steps: {', '.join(recipe.get('steps', []))}
        
        {validation_rules}
        
        IMPORTANT: If the recipe is INVALID, suggest 1-2 common ingredients that could help create a valid recipe.
        
        Return JSON:
        {{
            "valid": true/false,
            "reasoning": "Detailed explanation including difficulty assessment",
            "suggested_extras": ["ingredient1", "ingredient2"]  // Only if invalid, max 2 suggestions
        }}
        """
        
        try:
            response = self.llm.invoke(prompt)
            return self._parse_validation_response(response.content)
        except Exception as e:
            # Return conservative failure response on any error
            return {
                "valid": False,
                "reasoning": f"Validation error: {str(e)}",
                "suggested_extras": []
            }

