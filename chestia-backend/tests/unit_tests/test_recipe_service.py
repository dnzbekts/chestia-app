"""
Unit tests for RecipeService.

Tests the service layer's business logic and coordination between
domain, workflow, and infrastructure layers.
"""

import pytest
from unittest.mock import patch, MagicMock, call
from src.services import get_recipe_service, RecipeService


def test_singleton_pattern():
    """Test that get_recipe_service returns the same instance."""
    service1 = get_recipe_service()
    service2 = get_recipe_service()
    
    assert service1 is service2
    assert isinstance(service1, RecipeService)


@patch('src.services.recipe_service.get_db_connection')
@patch('src.services.recipe_service.db_save_recipe')
def test_save_generated_recipe_success(mock_db_save, mock_db_conn):
    """Test successful save of generated recipe."""
    # Setup
    mock_conn = MagicMock()
    mock_db_conn.return_value.__enter__.return_value = mock_conn
    mock_db_save.return_value = 123
    
    recipe = {
        "name": "Test Recipe",
        "steps": ["step1", "step2"],
        "metadata": {"source": "test"}
    }
    
    service = get_recipe_service()
    
    # Execute
    result = service.save_generated_recipe(
        recipe=recipe,
        ingredients=["chicken", "tomato"],
        difficulty="easy",
        lang="en",
        source_node="generate"
    )
    
    # Verify
    assert result == 123
    mock_db_save.assert_called_once_with(
        mock_conn,
        name="Test Recipe",
        ingredients=["chicken", "tomato"],
        difficulty="easy",
        lang="en",
        steps=["step1", "step2"],
        metadata={"source": "test"}
    )


@patch('src.services.recipe_service.get_db_connection')
@patch('src.services.recipe_service.db_save_recipe')
def test_save_generated_recipe_cache_skip(mock_db_save, mock_db_conn):
    """Test that cache hits are not saved."""
    recipe = {
        "name": "Cached Recipe",
        "steps": ["step1"],
        "metadata": {}
    }
    
    service = get_recipe_service()
    
    # Execute with cache source
    result = service.save_generated_recipe(
        recipe=recipe,
        ingredients=["pasta"],
        difficulty="easy",
        lang="en",
        source_node="cache"
    )
    
    # Verify
    assert result is None
    mock_db_save.assert_not_called()
    mock_db_conn.assert_not_called()


@patch('src.services.recipe_service.get_db_connection')
@patch('src.services.recipe_service.db_save_recipe')
def test_save_generated_recipe_semantic_skip(mock_db_save, mock_db_conn):
    """Test that semantic search hits are not saved."""
    recipe = {
        "name": "Semantic Recipe",
        "steps": ["step1"],
        "metadata": {}
    }
    
    service = get_recipe_service()
    
    # Execute with semantic source
    result = service.save_generated_recipe(
        recipe=recipe,
        ingredients=["pasta"],
        difficulty="easy",
        lang="en",
        source_node="semantic_search"
    )
    
    # Verify
    assert result is None
    mock_db_save.assert_not_called()
    mock_db_conn.assert_not_called()


@patch('src.services.recipe_service.get_db_connection')
@patch('src.services.recipe_service.db_save_recipe')
def test_save_generated_recipe_web_search(mock_db_save, mock_db_conn):
    """Test that web search results are saved."""
    mock_conn = MagicMock()
    mock_db_conn.return_value.__enter__.return_value = mock_conn
    mock_db_save.return_value = 456
    
    recipe = {
        "name": "Web Recipe",
        "steps": ["step1"],
        "metadata": {}
    }
    
    service = get_recipe_service()
    
    # Execute with web_search source
    result = service.save_generated_recipe(
        recipe=recipe,
        ingredients=["fish"],
        difficulty="hard",
        lang="tr",
        source_node="web_search"
    )
    
    # Verify
    assert result == 456
    mock_db_save.assert_called_once()


@patch('src.services.recipe_service.get_db_connection')
@patch('src.services.recipe_service.db_save_recipe')
def test_save_generated_recipe_json_metadata(mock_db_save, mock_db_conn):
    """Test handling of JSON string metadata."""
    mock_conn = MagicMock()
    mock_db_conn.return_value.__enter__.return_value = mock_conn
    mock_db_save.return_value = 789
    
    recipe = {
        "name": "JSON Recipe",
        "steps": ["step1"],
        "metadata": '{"key": "value"}'  # JSON string
    }
    
    service = get_recipe_service()
    
    # Execute
    result = service.save_generated_recipe(
        recipe=recipe,
        ingredients=["beef"],
        difficulty="intermediate",
        lang="en",
        source_node="generate"
    )
    
    # Verify metadata was parsed
    assert result == 789
    call_args = mock_db_save.call_args
    assert call_args[1]["metadata"] == {"key": "value"}


@patch('src.services.recipe_service.get_db_connection')
@patch('src.services.recipe_service.db_save_recipe')
@patch('src.services.recipe_service.filter_default_ingredients')
def test_save_approved_recipe(mock_filter, mock_db_save, mock_db_conn):
    """Test saving user-approved recipe with ingredient filtering."""
    mock_conn = MagicMock()
    mock_db_conn.return_value.__enter__.return_value = mock_conn
    mock_db_save.return_value = 999
    mock_filter.return_value = ["chicken", "tomato"]
    
    recipe_dict = {
        "name": "Approved Recipe",
        "steps": ["cook it"],
        "metadata": {"rating": 5}
    }
    
    service = get_recipe_service()
    
    # Execute
    result = service.save_approved_recipe(
        recipe_dict=recipe_dict,
        ingredients=["chicken", "tomato", "salt", "water"],
        difficulty="easy",
        lang="en"
    )
    
    # Verify
    assert result == 999
    mock_filter.assert_called_once_with(["chicken", "tomato", "salt", "water"])
    mock_db_save.assert_called_once_with(
        mock_conn,
        name="Approved Recipe",
        ingredients=["chicken", "tomato"],  # Filtered
        difficulty="easy",
        lang="en",
        steps=["cook it"],
        metadata={"rating": 5}
    )


@patch('src.services.recipe_service.get_db_connection')
@patch('src.services.recipe_service.db_find_by_ingredients')
def test_find_recipe_by_ingredients(mock_db_find, mock_db_conn):
    """Test finding recipe by exact ingredients."""
    mock_conn = MagicMock()
    mock_db_conn.return_value.__enter__.return_value = mock_conn
    mock_db_find.return_value = {"id": 1, "name": "Found Recipe"}
    
    service = get_recipe_service()
    
    # Execute
    result = service.find_recipe_by_ingredients(
        ingredients=["pasta", "cheese"],
        difficulty="easy",
        lang="en"
    )
    
    # Verify
    assert result == {"id": 1, "name": "Found Recipe"}
    mock_db_find.assert_called_once_with(
        mock_conn,
        ["pasta", "cheese"],
        "easy",
        "en"
    )


@patch('src.services.recipe_service.get_db_connection')
@patch('src.services.recipe_service.db_find_semantically')
def test_find_recipe_semantically(mock_db_find, mock_db_conn):
    """Test finding recipe by semantic similarity."""
    mock_conn = MagicMock()
    mock_db_conn.return_value.__enter__.return_value = mock_conn
    mock_db_find.return_value = {"id": 2, "name": "Similar Recipe"}
    
    service = get_recipe_service()
    
    # Execute
    result = service.find_recipe_semantically(
        ingredients=["noodles", "parmesan"],
        difficulty="intermediate",
        lang="tr",
        threshold=0.8
    )
    
    # Verify
    assert result == {"id": 2, "name": "Similar Recipe"}
    mock_db_find.assert_called_once_with(
        mock_conn,
        ["noodles", "parmesan"],
        "intermediate",
        "tr",
        0.8
    )


@patch('src.services.recipe_service.get_db_connection')
@patch('src.services.recipe_service.db_log_error')
def test_log_error(mock_db_log, mock_db_conn):
    """Test error logging to database."""
    mock_conn = MagicMock()
    mock_db_conn.return_value.__enter__.return_value = mock_conn
    
    service = get_recipe_service()
    
    # Execute
    service.log_error(
        error_type="TestError",
        message="Something went wrong",
        request_id="req-123"
    )
    
    # Verify
    mock_db_log.assert_called_once_with(
        mock_conn,
        "TestError",
        "Something went wrong",
        "req-123"
    )


@patch('src.services.recipe_service.get_db_connection')
@patch('src.services.recipe_service.db_log_error')
def test_log_error_failure_handling(mock_db_log, mock_db_conn):
    """Test that log_error handles database failures gracefully."""
    mock_db_log.side_effect = Exception("Database error")
    
    service = get_recipe_service()
    
    # Execute - should not raise exception
    service.log_error("TestError", "Test message")
    
    # Verify it attempted to log
    mock_db_log.assert_called_once()
