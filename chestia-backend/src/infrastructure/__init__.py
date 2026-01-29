"""
Infrastructure layer - External services: database, LLM, localization.
"""

from .database import (
    get_db_connection,
    init_db,
    find_recipe_by_ingredients,
    find_recipe_semantically,
    save_recipe,
    log_error,
)
from .llm_factory import LLMFactory

__all__ = [
    "get_db_connection",
    "init_db",
    "find_recipe_by_ingredients",
    "find_recipe_semantically",
    "save_recipe",
    "log_error",
    "LLMFactory",
]
