"""
Recipe Agent - Generates recipes using LLM based on user ingredients.

Refactored to use LLMFactory for initialization and follow DRY/SOLID principles.
"""

from typing import List, Dict, Any
import json
import logging
from src.infrastructure.llm_factory import LLMFactory
from src.core.exceptions import RecipeGenerationError, IngredientValidationError



logger = logging.getLogger(__name__)


class RecipeAgent:
    """Agent responsible for generating recipes from ingredients."""
    
    def __init__(self):
        """Initialize the RecipeAgent with configured LLM."""
        self.llm = LLMFactory.create_recipe_llm()

    def _sanitize_ingredients(self, ingredients: List[str]) -> List[str]:
        """
        Strict input validation for ingredients.
        
        Args:
            ingredients: Raw ingredient list
            
        Returns:
            Sanitized ingredient list
            
        Raises:
            IngredientValidationError: If no valid ingredients remain
        """
        sanitized = []
        for ing in ingredients:
            # Skip empty or whitespace-only strings
            if not ing or not ing.strip():
                continue
                
            # Remove any non-alphanumeric chars except space/comma/dash
            clean = "".join(
                char for char in ing 
                if char.isalnum() or char in " ,-"
            ).strip()
            
            # Validate cleaned ingredient
            if clean and len(clean) < 50:
                sanitized.append(clean)
        
        return sanitized

    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """
        Parse JSON response from LLM, handling markdown code blocks.
        
        Args:
            content: Raw LLM response content
            
        Returns:
            Parsed JSON dictionary
            
        Raises:
            RecipeGenerationError: If JSON parsing fails
        """
        try:
            # Remove markdown code block markers
            cleaned = content.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise RecipeGenerationError(
                f"Failed to parse recipe JSON: {e}",
                details={"raw_content": content[:200]}
            )

    def generate(self, ingredients: List[str], difficulty: str, lang: str = "en") -> Dict[str, Any]:
        """
        Generate a recipe from user-provided ingredients at specified difficulty.
        Default household ingredients are assumed available.
        
        Args:
            ingredients: User's ingredient list
            difficulty: Recipe difficulty ('easy', 'intermediate', 'hard')
            
        Returns:
            Recipe dictionary with name, ingredients, steps, and metadata
            
        Raises:
            IngredientValidationError: If no valid ingredients after sanitization
            RecipeGenerationError: If recipe generation fails
        """
        from src.domain.ingredients import DEFAULT_INGREDIENTS
        
        # Sanitize and validate ingredients
        ingredients = self._sanitize_ingredients(ingredients)
        if not ingredients:
            raise IngredientValidationError(
                "No valid ingredients provided after sanitization"
            )
        
        # Format default ingredients for prompt
        default_ingredients_list = ', '.join(sorted(DEFAULT_INGREDIENTS))
        
        # Difficulty-specific instructions
        difficulty_guidance = {
            "easy": "Simple techniques, minimal prep, 15-30 min total time, beginner-friendly",
            "intermediate": "Moderate techniques, some prep required, 30-60 min, home cook level",
            "hard": "Advanced techniques, significant prep, 60+ min, experienced cook level"
        }
        
        prompt = f"""
        You are a professional chef creating a recipe.
        
        AVAILABLE INGREDIENTS:
        - User's Ingredients: {', '.join(ingredients)}
        - Default Ingredients (always available): {default_ingredients_list}
        
        Difficulty Level: {difficulty.upper()} - {difficulty_guidance.get(difficulty, '')}
        Language: {lang.upper()}
        
        STRICT RULES (MUST FOLLOW):
        1. You MUST ONLY use ingredients from the lists above
        2. Do NOT add ANY ingredient that is not in User's Ingredients or Default Ingredients
        3. This is a hard constraint - violation means the recipe is invalid
        4. ALL text fields (name, ingredients, steps) MUST be in {lang.upper()} language.
        
        Recipe Guidelines:
        1. Create a {difficulty} difficulty recipe using ONLY the available ingredients
        2. Ensure the recipient can understand the recipe in {lang.upper()}.
        3. Match complexity to {difficulty} level:
           - Easy: Simple steps, basic techniques, 15-30 min
           - Intermediate: Multiple steps, some technique required, 30-60 min
           - Hard: Complex techniques, multiple stages, 60+ min
        
        Return JSON:
        {{
            "name": "Recipe Name in {lang.upper()}",
            "ingredients": ["list", "of", "ingredients", "in", "{lang.upper()}"],
            "steps": ["step1", "step2", ...],
            "metadata": {{"time": "20min", "difficulty": "{difficulty}"}}
        }}
        """
        
        try:
            response = self.llm.invoke(prompt)
            return self._parse_json_response(response.content)
        except Exception as e:
            if isinstance(e, (RecipeGenerationError, IngredientValidationError)):
                raise
            raise RecipeGenerationError(
                f"Unexpected error during recipe generation: {str(e)}"
            )
    def parse_request(self, messages: List[Any]) -> Dict[str, Any]:
        """
        Parse user request from conversation history to extract ingredients and difficulty.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            Dictionary with keys: ingredients, difficulty, lang (inferred)
        """
        if not messages:
            return {}
            
        # Get the last user message
        last_message = None
        for msg in reversed(messages):
            if hasattr(msg, "type") and msg.type == "human":
                last_message = msg.content
                break
            # Handle dict messages (if raw)
            elif isinstance(msg, dict) and msg.get("type") == "human":
                last_message = msg.get("content")
                break
                
        if not last_message:
            return {}

        prompt = f"""
        Extract cooking parameters from the user's request.
        
        USER REQUEST: "{last_message}"
        
        Extact:
        1. Ingredients (list of strings)
        2. Difficulty (easy/intermediate/hard) - default to 'easy' if not specified
        3. Language (en/tr) - detect from text
        
        Output JSON only:
        {{
            "ingredients": ["ing1", "ing2"],
            "difficulty": "easy",
            "lang": "en"
        }}
        """
        
        try:
            response = self.llm.invoke(prompt)
            return self._parse_json_response(response.content)
        except Exception as e:
            logger.error(f"Failed to parse user request: {e}")
            return {}
