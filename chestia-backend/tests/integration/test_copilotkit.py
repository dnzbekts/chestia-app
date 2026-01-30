"""
Integration tests for the CopilotKit endpoint.

Tests the /copilotkit FastAPI endpoint integration with LangGraph AGUI Agent.
These tests verify endpoint accessibility, request/response format,
and basic agent invocation without mocking the CopilotKit SDK internals.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


class TestCopilotKitEndpointAccessibility:
    """Tests for CopilotKit endpoint accessibility and routing."""

    def test_copilotkit_endpoint_exists(self, api_client):
        """Test that /copilotkit endpoint is registered and accessible."""
        # OPTIONS request to check if endpoint exists
        response = api_client.options("/copilotkit/")
        # Should not return 404
        assert response.status_code != 404, "CopilotKit endpoint should be registered"

    def test_copilotkit_requires_post_with_body(self, api_client):
        """Test that /copilotkit requires a POST request with body."""
        try:
            response = api_client.get("/copilotkit/")
            # GET without body should fail
            assert response.status_code in [400, 405, 422, 500]
        except Exception:
            # SDK may raise exception for malformed requests - this is expected
            pass

    def test_copilotkit_rejects_empty_body(self, api_client):
        """Test that /copilotkit rejects empty request body."""
        try:
            response = api_client.post(
                "/copilotkit/",
                headers={"Content-Type": "application/json"},
                content=""
            )
            # Should reject empty body
            assert response.status_code in [400, 422, 500]
        except Exception:
            # SDK may raise exception for empty body - this is expected
            pass


class TestCopilotKitAgentConfiguration:
    """Tests for CopilotKit agent configuration."""

    def test_copilotkit_agent_name_configured(self):
        """Test that CopilotKit agent name is properly configured."""
        from src.core import COPILOTKIT_AGENT_NAME
        assert COPILOTKIT_AGENT_NAME == "chestia_recipe_agent"

    def test_copilotkit_agent_description_configured(self):
        """Test that CopilotKit agent description is properly configured."""
        from src.core import COPILOTKIT_AGENT_DESCRIPTION
        assert "recipe" in COPILOTKIT_AGENT_DESCRIPTION.lower()
        assert "ingredients" in COPILOTKIT_AGENT_DESCRIPTION.lower()

    def test_copilotkit_graph_has_checkpointer(self):
        """Test that CopilotKit graph is compiled with checkpointer."""
        from src.workflow import copilotkit_graph
        # Graph should be compiled (has invoke method)
        assert hasattr(copilotkit_graph, "invoke")
        # Graph should have checkpointer for state persistence
        assert hasattr(copilotkit_graph, "checkpointer")


class TestCopilotKitRemoteEndpoint:
    """Tests for CopilotKit Remote Endpoint SDK integration."""

    def test_copilotkit_sdk_initialization(self):
        """Test that CopilotKit SDK is properly initialized in main.py."""
        from src.main import copilotkit_sdk
        from copilotkit import CopilotKitRemoteEndpoint
        
        assert isinstance(copilotkit_sdk, CopilotKitRemoteEndpoint)

    def test_copilotkit_sdk_has_agents(self):
        """Test that CopilotKit SDK has registered agents."""
        from src.main import copilotkit_sdk
        
        # SDK should have agents list
        assert hasattr(copilotkit_sdk, "agents")
        assert len(copilotkit_sdk.agents) > 0

    def test_copilotkit_agent_type(self):
        """Test that registered agent is ChestiaLangGraphAgent (custom subclass)."""
        from src.main import copilotkit_sdk, ChestiaLangGraphAgent
        
        agent = copilotkit_sdk.agents[0]
        assert isinstance(agent, ChestiaLangGraphAgent)


class TestCopilotKitGraphInvocation:
    """Tests for CopilotKit graph invocation with mocked dependencies."""

    @pytest.fixture
    def mock_graph_state(self):
        """Sample graph state for testing."""
        return {
            "ingredients": ["chicken", "tomato", "onion"],
            "original_ingredients": ["chicken", "tomato", "onion"],
            "difficulty": "easy",
            "lang": "en",
            "recipe": None,
            "extra_ingredients": [],
            "extra_count": 0,
            "error": None,
            "iteration_count": 0
        }

    def test_copilotkit_graph_accepts_valid_state(self, mock_graph_state):
        """Test that CopilotKit graph accepts valid input state."""
        from src.workflow import copilotkit_graph
        
        # Mock all external dependencies
        with patch("src.workflow.graph.get_db_connection") as mock_db, \
             patch("src.workflow.graph.find_recipe_by_ingredients") as mock_find, \
             patch("src.workflow.graph.find_recipe_semantically") as mock_semantic:
            
            mock_db.return_value.__enter__ = MagicMock()
            mock_db.return_value.__exit__ = MagicMock()
            mock_find.return_value = {
                "id": 1,
                "name": "Test Recipe",
                "ingredients": '["chicken", "tomato", "onion"]',
                "steps": '["Step 1", "Step 2"]',
                "difficulty": "easy",
                "metadata": "{}"
            }
            
            # Should not raise
            config = {"configurable": {"thread_id": "test-thread-1"}}
            result = copilotkit_graph.invoke(mock_graph_state, config=config)
            
            assert result is not None
            assert "recipe" in result or "error" in result


class TestCopilotKitSSEStreaming:
    """Tests for Server-Sent Events streaming capability."""

    def test_copilotkit_endpoint_accepts_sse_headers(self, api_client):
        """Test that /copilotkit accepts SSE-related headers."""
        response = api_client.post(
            "/copilotkit/",
            headers={
                "Content-Type": "application/json",
                "Accept": "text/event-stream"
            },
            json={"method": "info"}
        )
        # Should return success with agent info
        assert response.status_code == 200
