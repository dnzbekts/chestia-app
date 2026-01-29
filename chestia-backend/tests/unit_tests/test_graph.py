import pytest
from src.workflow.graph import add_extras, RecipeGraphOrchestrator

def test_add_extras_reducer():
    """Test the LangGraph state reducer for extras."""
    existing = ["salt", "pepper"]
    new = ["garlic"]
    result = add_extras(existing, new)
    assert result == ["salt", "pepper", "garlic"]

def test_route_after_review_end_on_error():
    """Test routing to END if error present."""
    orchestrator = RecipeGraphOrchestrator()
    state = {"error": "some error"}
    assert orchestrator.route_after_review(state) == "__end__"

def test_route_after_review_retry():
    """Test routing back to generate if recipe is missing and iterations remain."""
    orchestrator = RecipeGraphOrchestrator()
    state = {"recipe": None, "iteration_count": 0, "error": None}
    assert orchestrator.route_after_review(state) == "generate"

def test_route_after_cache_hit():
    """Test routing after cache hit."""
    orchestrator = RecipeGraphOrchestrator()
    state = {"recipe": {"name": "Test"}}
    assert orchestrator.route_after_cache(state) == "review_recipe"

def test_route_after_cache_miss():
    """Test routing after cache miss."""
    orchestrator = RecipeGraphOrchestrator()
    state = {"recipe": None}
    assert orchestrator.route_after_cache(state) == "semantic_search"
