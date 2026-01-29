import pytest
from src.core.exceptions import (
    ChestiaBaseException,
    RecipeGenerationError,
    RecipeValidationError,
    IngredientValidationError,
    DatabaseError,
    EmbeddingGenerationError,
    SearchError,
    ConfigurationError
)

def test_base_exception_init():
    """Test base exception with message and details."""
    details = {"code": 404, "source": "api"}
    exc = ChestiaBaseException("Test error", details=details)
    assert str(exc) == "Test error"
    assert exc.message == "Test error"
    assert exc.details == details

def test_exception_subclasses():
    """Test that subclasses initialize correctly."""
    exceptions = [
        (RecipeGenerationError, "generation failed"),
        (RecipeValidationError, "invalid structure"),
        (IngredientValidationError, "bad ingredients"),
        (DatabaseError, "db error"),
        (EmbeddingGenerationError, "embedding failed"),
        (SearchError, "search failed"),
        (ConfigurationError, "config missing")
    ]
    
    for exc_class, msg in exceptions:
        inst = exc_class(msg)
        assert isinstance(inst, ChestiaBaseException)
        assert inst.message == msg
        assert inst.details == {}

def test_embedding_error_inheritance():
    """Test specific inheritance for embedding error."""
    exc = EmbeddingGenerationError("failed")
    assert isinstance(exc, DatabaseError)
    assert isinstance(exc, ChestiaBaseException)
