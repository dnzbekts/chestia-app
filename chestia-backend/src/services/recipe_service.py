"""
Recipe business logic and orchestration.

Coordinates between domain, workflow, and infrastructure layers.
Follows Clean Architecture principles by separating business logic
from API routes and infrastructure concerns.
"""

from typing import Dict, Any, List, Optional
import logging
import json

from src.infrastructure.database import (
    get_db_connection,
    save_recipe as db_save_recipe,
    log_error as db_log_error,
    find_recipe_by_ingredients as db_find_by_ingredients,
    find_recipe_semantically as db_find_semantically,
)
from src.domain.ingredients import filter_default_ingredients

logger = logging.getLogger(__name__)


class RecipeService:
    """
    Service layer for recipe operations.
    
    Responsibilities:
    - Coordinate recipe generation workflow
    - Handle recipe persistence logic (save operations)
    - Handle recipe retrieval logic (find operations)
    - Manage error logging
    - Filter and validate ingredients
    
    This service is stateless and uses singleton pattern for efficiency.
    """
    
    def save_generated_recipe(
        self,
        recipe: Dict[str, Any],
        ingredients: List[str],
        difficulty: str,
        lang: str,
        source_node: str
    ) -> Optional[int]:
        """
        Save a newly generated or web-searched recipe.
        
        Only saves recipes from 'generate' or 'web_search' nodes,
        not from cache or semantic search.
        
        Args:
            recipe: Recipe dictionary with name, steps, metadata
            ingredients: List of ingredients used
            difficulty: Recipe difficulty level
            lang: Recipe language
            source_node: Source node that generated the recipe
            
        Returns:
            Recipe ID if saved, None if skipped or failed
        """
        # Only save newly created recipes
        if source_node not in ("generate", "web_search"):
            logger.debug(f"Skipping save for source_node={source_node}")
            return None
        
        try:
            metadata = recipe.get("metadata", {})
            if isinstance(metadata, str):
                metadata = json.loads(metadata)
            
            with get_db_connection() as conn:
                recipe_id = db_save_recipe(
                    conn,
                    name=recipe["name"],
                    ingredients=ingredients,
                    difficulty=difficulty,
                    lang=lang,
                    steps=recipe["steps"],
                    metadata=metadata
                )
            
            logger.info(f"Successfully saved recipe: {recipe['name']} (ID: {recipe_id})")
            return recipe_id
            
        except Exception as e:
            logger.warning(f"Failed to save recipe: {e}")
            return None
    
    def save_approved_recipe(
        self,
        recipe_dict: Dict[str, Any],
        ingredients: List[str],
        difficulty: str,
        lang: str
    ) -> int:
        """
        Save a user-approved recipe from feedback.
        
        Filters default ingredients before saving.
        
        Args:
            recipe_dict: Recipe dictionary
            ingredients: Original ingredients list
            difficulty: Recipe difficulty
            lang: Recipe language
            
        Returns:
            Recipe ID
            
        Raises:
            Exception: If save fails
        """
        # Filter default ingredients before caching
        non_default_ingredients = filter_default_ingredients(ingredients)
        
        with get_db_connection() as conn:
            return db_save_recipe(
                conn,
                name=recipe_dict["name"],
                ingredients=non_default_ingredients,
                difficulty=difficulty,
                lang=lang,
                steps=recipe_dict["steps"],
                metadata=recipe_dict.get("metadata", {})
            )
    
    def find_recipe_by_ingredients(
        self,
        ingredients: List[str],
        difficulty: str,
        lang: str = "en"
    ) -> Optional[Dict[str, Any]]:
        """
        Find a recipe matching exact ingredients and difficulty.
        
        Args:
            ingredients: List of ingredient names
            difficulty: Recipe difficulty level
            lang: Recipe language
            
        Returns:
            Recipe dict if found, None otherwise
        """
        with get_db_connection() as conn:
            return db_find_by_ingredients(conn, ingredients, difficulty, lang)
    
    def find_recipe_semantically(
        self,
        ingredients: List[str],
        difficulty: str,
        lang: str = "en",
        threshold: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Find a recipe using semantic similarity on ingredients.
        
        Args:
            ingredients: List of ingredients
            difficulty: Recipe difficulty level
            lang: Recipe language
            threshold: Optional similarity threshold
            
        Returns:
            Recipe dict if found, None otherwise
        """
        with get_db_connection() as conn:
            return db_find_semantically(conn, ingredients, difficulty, lang, threshold)
    
    def log_error(
        self,
        error_type: str,
        message: str,
        request_id: Optional[str] = None
    ) -> None:
        """
        Log an error to the database.
        
        Args:
            error_type: Type of error (e.g., 'GenerationError')
            message: Error message
            request_id: Optional request identifier
        """
        try:
            with get_db_connection() as conn:
                db_log_error(conn, error_type, message, request_id)
        except Exception as e:
            logger.error(f"Failed to log error to database: {e}")
