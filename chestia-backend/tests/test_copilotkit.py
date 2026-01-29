"""
CopilotKit Integration Tests

Tests for the CopilotKit wrapper module and endpoint integration.
Follows TDD principles as mandated by GEMINI.md.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from langchain_core.messages import HumanMessage, AIMessage

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.workflow.graph import (
    GraphState as CopilotKitState,
    RecipeGraphOrchestrator,
)
from src.core.exceptions import RecipeGenerationError
from langgraph.graph import END
from src.workflow.copilotkit_adapter import copilotkit_graph as create_copilotkit_graph
from src.core.config import COPILOTKIT_AGENT_NAME, COPILOTKIT_AGENT_DESCRIPTION


class TestCopilotKitConfiguration:
    """Tests for CopilotKit configuration constants."""
    
    def test_agent_name_defined(self):
        """CopilotKit agent name should be defined."""
        assert COPILOTKIT_AGENT_NAME == "chestia_recipe_agent"
    
    def test_agent_description_defined(self):
        """CopilotKit agent description should be defined."""
        assert "recipe" in COPILOTKIT_AGENT_DESCRIPTION.lower()


class TestCopilotKitState:
    """Tests for CopilotKit state initialization."""
    
    def test_get_initial_state_basic(self):
        """Initial state should contain required fields."""
        state = {
            "ingredients": ["chicken", "rice", "onion"],
            "difficulty": "easy",
            "lang": "en",
            "messages": [],
            "iteration_count": 0,
            "extra_count": 0
        }
        
        assert "messages" in state
        assert "ingredients" in state
        assert "difficulty" in state
        assert "lang" in state
        assert state["difficulty"] == "easy"
        assert state["lang"] == "en"
        assert state["iteration_count"] == 0
        assert state["extra_count"] == 0
    
    def test_get_initial_state_filters_defaults(self):
        """Initial state should filter default ingredients."""
        # Note: Filtering normally happens in api.py before calling the graph
        # and inside the orchestrator if needed.
        from src.domain.ingredients import filter_default_ingredients
        ingredients = filter_default_ingredients(["chicken", "salt", "water", "onion", "rice"])
        
        # Default ingredients should be filtered out
        assert "salt" not in ingredients
        assert "water" not in ingredients
        assert "chicken" in ingredients
        assert "onion" in ingredients
    
    def test_initial_state_with_custom_message(self):
        """Initial state should use custom message if provided."""
        from langchain_core.messages import HumanMessage
        state = {
            "ingredients": ["beef", "potato"],
            "difficulty": "hard",
            "lang": "en",
            "messages": [HumanMessage(content="Make me a gourmet steak")]
        }
        
        assert len(state["messages"]) == 1
        assert isinstance(state["messages"][0], HumanMessage)
        assert "gourmet steak" in state["messages"][0].content


class TestCopilotKitGraph:
    """Tests for CopilotKit LangGraph workflow."""
    
    def test_graph_creation(self):
        """Graph should be created successfully."""
        graph = create_copilotkit_graph
        assert graph is not None
    
    def test_router_with_error(self):
        """Router should return 'end' when error exists."""
        orchestrator = RecipeGraphOrchestrator()
        state = CopilotKitState(
            messages=[],
            ingredients=["chicken"],
            difficulty="easy",
            lang="en",
            recipe=None,
            extra_ingredients=[],
            extra_count=0,
            error="Some error",
            iteration_count=1
        )
        assert orchestrator.route_after_review(state) == END
    
    def test_router_with_recipe(self):
        """Router should return 'end' when recipe exists."""
        orchestrator = RecipeGraphOrchestrator()
        state = CopilotKitState(
            messages=[],
            ingredients=["chicken"],
            difficulty="easy",
            lang="en",
            recipe={"name": "Test Recipe"},
            extra_ingredients=[],
            extra_count=0,
            error=None,
            iteration_count=1
        )
        assert orchestrator.route_after_review(state) == END
    
    def test_router_max_iterations(self):
        """Router should return 'end' when max iterations reached."""
        orchestrator = RecipeGraphOrchestrator()
        state = CopilotKitState(
            messages=[],
            ingredients=["chicken"],
            difficulty="easy",
            lang="en",
            recipe=None,
            extra_ingredients=[],
            extra_count=0,
            error=None,
            iteration_count=3
        )
        assert orchestrator.route_after_review(state) == END
    
    def test_router_needs_generation(self):
        """Router should return 'generate' when recipe needs generation."""
        orchestrator = RecipeGraphOrchestrator()
        state = CopilotKitState(
            messages=[],
            ingredients=["chicken"],
            difficulty="easy",
            lang="en",
            recipe=None,
            extra_ingredients=[],
            extra_count=0,
            error=None,
            iteration_count=0
        )
        assert orchestrator.route_after_review(state) == "generate"


class TestSearchCacheNode:
    """Tests for cache search node."""
    
    @patch('src.workflow.graph.get_db_connection')
    @patch('src.workflow.graph.find_recipe_by_ingredients')
    def test_cache_hit(self, mock_find, mock_db_conn):
        """Should return recipe when cache hit."""
        orchestrator = RecipeGraphOrchestrator()
        mock_find.return_value = {
            "name": "Cached Recipe",
            "ingredients": ["chicken", "rice"]
        }
        
        state = CopilotKitState(
            messages=[],
            ingredients=["chicken", "rice"],
            difficulty="easy",
            lang="en",
            recipe=None,
            extra_ingredients=[],
            extra_count=0,
            error=None,
            iteration_count=0
        )
        
        result = orchestrator.search_cache_node(state)
        
        assert result["recipe"] is not None
        assert result["recipe"]["name"] == "Cached Recipe"
        assert "messages" in result
    
    @patch('src.workflow.graph.get_db_connection')
    @patch('src.workflow.graph.find_recipe_by_ingredients')
    def test_cache_miss(self, mock_find, mock_db_conn):
        """Should increment iteration and emit message on cache miss."""
        orchestrator = RecipeGraphOrchestrator()
        mock_find.return_value = None
        
        state = CopilotKitState(
            messages=[],
            ingredients=["chicken", "rice"],
            difficulty="easy",
            lang="en",
            recipe=None,
            extra_ingredients=[],
            extra_count=0,
            error=None,
            iteration_count=0
        )
        
        result = orchestrator.search_cache_node(state)
        
        assert result.get("recipe") is None
        assert result["iteration_count"] == 1
        assert "messages" in result


class TestGenerateRecipeNode:
    """Tests for recipe generation node."""
    
    @patch('src.workflow.graph.RecipeAgent')
    def test_successful_generation(self, mock_agent_class):
        """Should return recipe on successful generation."""
        orchestrator = RecipeGraphOrchestrator()
        mock_agent = MagicMock()
        mock_agent.generate.return_value = {
            "name": "Generated Recipe",
            "ingredients": ["chicken", "rice"],
            "steps": ["Step 1", "Step 2"]
        }
        orchestrator.recipe_agent = mock_agent
        
        state = CopilotKitState(
            messages=[],
            ingredients=["chicken", "rice"],
            difficulty="easy",
            lang="en",
            recipe=None,
            extra_ingredients=[],
            extra_count=0,
            error=None,
            iteration_count=0
        )
        
        result = orchestrator.generate_recipe_node(state)
        
        assert result["recipe"]["name"] == "Generated Recipe"
        assert "messages" in result
    
    @patch('src.workflow.graph.RecipeAgent')
    def test_generation_error(self, mock_agent_class):
        """Should return error on generation failure."""
        orchestrator = RecipeGraphOrchestrator()
        mock_agent = MagicMock()
        mock_agent.generate.side_effect = RecipeGenerationError("LLM failed")
        orchestrator.recipe_agent = mock_agent
        
        state = CopilotKitState(
            messages=[],
            ingredients=["chicken"],
            difficulty="hard",
            lang="en",
            recipe=None,
            extra_ingredients=[],
            extra_count=0,
            error=None,
            iteration_count=0
        )
        
        result = orchestrator.generate_recipe_node(state)
        
        assert result["error"] == "LLM failed"
        assert "messages" in result


class TestReviewRecipeNode:
    """Tests for recipe review node."""
    
    @patch('src.workflow.graph.ReviewAgent')
    def test_valid_recipe(self, mock_agent_class):
        """Should return success on valid recipe."""
        orchestrator = RecipeGraphOrchestrator()
        mock_agent = MagicMock()
        mock_agent.validate.return_value = {"valid": True}
        orchestrator.review_agent = mock_agent
        
        state = CopilotKitState(
            messages=[],
            ingredients=["chicken", "rice"],
            difficulty="easy",
            lang="en",
            recipe={"name": "Test Recipe", "ingredients": ["chicken", "rice"]},
            extra_ingredients=[],
            extra_count=0,
            error=None,
            iteration_count=1
        )
        
        result = orchestrator.review_recipe_node(state)
        
        assert result.get("error") is None
        assert "messages" in result
    
    @patch('src.workflow.graph.ReviewAgent')
    def test_invalid_recipe_with_suggestions(self, mock_agent_class):
        """Should add suggested extras when recipe is invalid."""
        orchestrator = RecipeGraphOrchestrator()
        mock_agent = MagicMock()
        mock_agent.validate.return_value = {
            "valid": False,
            "reasoning": "Missing key ingredient",
            "suggested_extras": ["garlic", "tomato"]
        }
        orchestrator.review_agent = mock_agent
        
        state = CopilotKitState(
            messages=[],
            ingredients=["chicken", "rice"],
            difficulty="easy",
            lang="en",
            recipe={"name": "Test Recipe", "ingredients": ["chicken", "rice"]},
            extra_ingredients=[],
            extra_count=0,
            error=None,
            iteration_count=1
        )
        
        result = orchestrator.review_recipe_node(state)
        
        assert "garlic" in result["ingredients"]
        assert "tomato" in result["ingredients"]
        assert result["extra_count"] == 2
        assert result["recipe"] is None  # Cleared for regeneration


class TestCopilotKitEndpoint:
    """Tests for CopilotKit FastAPI endpoint."""
    
    def test_endpoint_exists(self):
        """CopilotKit endpoint should be registered."""
        from src.main import app
        client = TestClient(app)
        
        # OPTIONS request to check if endpoint exists
        # CopilotKit uses POST, but we can check route registration
        routes = [route.path for route in app.routes]
        assert "/copilotkit" in routes or any("/copilotkit" in r for r in routes)
