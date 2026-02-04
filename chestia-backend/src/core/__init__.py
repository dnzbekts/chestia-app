"""
Core layer - Cross-cutting concerns: config, exceptions, logging.
"""

from .config import (
    LLM_CONFIG,
    SEARCH_CONFIG,
    GRAPH_CONFIG,
    DB_CONFIG,
)
from .exceptions import (
    ChestiaBaseException,
    RecipeGenerationError,
    RecipeValidationError,
    IngredientValidationError,
    DatabaseError,
    EmbeddingGenerationError,
    SearchError,
    ConfigurationError,
)
from .logging_config import setup_logging

__all__ = [
    "LLM_CONFIG",
    "SEARCH_CONFIG",
    "GRAPH_CONFIG",
    "DB_CONFIG",
    "ChestiaBaseException",
    "RecipeGenerationError",
    "RecipeValidationError",
    "IngredientValidationError",
    "DatabaseError",
    "EmbeddingGenerationError",
    "SearchError",
    "ConfigurationError",
    "setup_logging",
]
