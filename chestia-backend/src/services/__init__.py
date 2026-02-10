"""
Service layer - Business logic and orchestration.

Provides singleton access to service instances following the same
pattern as infrastructure layer (e.g., get_embedding_service).
"""

from .recipe_service import RecipeService

# Global singleton instance
_recipe_service = None


def get_recipe_service() -> RecipeService:
    """
    Get or create the global recipe service instance.
    
    Uses singleton pattern for efficiency and consistency.
    Service is stateless, so single instance is safe for concurrent requests.
    
    Returns:
        RecipeService singleton instance
    """
    global _recipe_service
    if _recipe_service is None:
        _recipe_service = RecipeService()
    return _recipe_service


__all__ = ["get_recipe_service", "RecipeService"]
