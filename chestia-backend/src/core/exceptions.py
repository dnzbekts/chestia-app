"""
Domain-specific exceptions for Chestia backend.

Following Clean Architecture principles, these exceptions provide clear,
domain-specific error handling throughout the application.
"""


class ChestiaBaseException(Exception):
    """Base exception for all Chestia-specific errors."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class RecipeGenerationError(ChestiaBaseException):
    """Raised when recipe generation fails."""
    pass


class RecipeValidationError(ChestiaBaseException):
    """Raised when recipe validation fails."""
    pass


class IngredientValidationError(ChestiaBaseException):
    """Raised when ingredient validation fails."""
    pass


class DatabaseError(ChestiaBaseException):
    """Raised when database operations fail."""
    pass


class EmbeddingGenerationError(DatabaseError):
    """Raised when embedding generation fails."""
    pass


class SearchError(ChestiaBaseException):
    """Raised when web search operations fail."""
    pass


class ConfigurationError(ChestiaBaseException):
    """Raised when configuration is invalid or missing."""
    pass
