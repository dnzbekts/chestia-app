import pytest
from unittest.mock import MagicMock, patch
import os
import sys

# Add src to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from agents.search_agent import SearchAgent
from graph import web_search_node, GraphState
from langchain_core.messages import AIMessage

class TestSearchAgent:
    @pytest.fixture
    def mock_env(self):
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "fake_key", "TAVILY_API_KEY": "fake_key"}):
            yield

    @pytest.fixture
    def mock_tavily(self):
        with patch('agents.search_agent.TavilySearchResults') as mock:
            yield mock

    @pytest.fixture
    def mock_llm(self):
        with patch('agents.search_agent.ChatGoogleGenerativeAI') as mock:
            yield mock

    def test_search_agent_query_construction(self, mock_env, mock_tavily, mock_llm):
        """Test that search query includes only allowed ingredients"""
        # Setup
        agent = SearchAgent()
        mock_tool = mock_tavily.return_value
        mock_tool.invoke.return_value = [{"content": "some recipe content"}]
        
        mock_llm_instance = mock_llm.return_value
        mock_llm_instance.invoke.return_value.content = '{"name": "Test Recipe", "ingredients": ["chicken"], "steps": [], "metadata": {}}'
        
        # Execute
        agent.search(ingredients=["chicken"], difficulty="easy")
        
        # Verify
        args, _ = mock_tool.invoke.call_args
        query = args[0]["query"]
        assert "chicken" in query
        assert "easy" in query
        assert "only" in query.lower() or "using" in query.lower()

    def test_search_agent_returns_none_context_on_failure(self, mock_env, mock_tavily, mock_llm):
        """Test fallback when no results found"""
        agent = SearchAgent()
        mock_tool = mock_tavily.return_value
        mock_tool.invoke.return_value = [] # Empty results
        
        result = agent.search(["chicken"], "easy")
        assert result is None

    def test_search_agent_parses_llm_output(self, mock_env, mock_tavily, mock_llm):
        """Test that raw search results are parsed into recipe dict"""
        agent = SearchAgent()
        mock_tool = mock_tavily.return_value
        mock_tool.invoke.return_value = [{"content": "Delicious Chicken Rice recipe..."}]
        
        mock_llm_instance = mock_llm.return_value
        mock_llm_instance.invoke.return_value.content = '''
        {
            "name": "Chicken Rice",
            "ingredients": ["chicken", "rice"],
            "steps": ["Boil chicken", "Cook rice"],
            "metadata": {"difficulty": "easy"}
        }
        '''
        
        result = agent.search(["chicken", "rice"], "easy")
        assert result["name"] == "Chicken Rice"
        assert len(result["steps"]) == 2


class TestWebSearchNode:
    @patch('graph.SearchAgent')
    def test_web_search_node_success(self, mock_search_agent_cls):
        """Test successful search updates state with recipe"""
        # Setup
        mock_agent = mock_search_agent_cls.return_value
        expected_recipe = {"name": "Found Recipe", "ingredients": [], "steps": []}
        mock_agent.search.return_value = expected_recipe
        
        state = {
            "ingredients": ["chicken"], 
            "difficulty": "easy",
            "iteration_count": 0
        }
        
        # Execute
        result = web_search_node(state)
        
        # Verify
        assert result["recipe"] == expected_recipe

    @patch('graph.SearchAgent')
    def test_web_search_node_failure(self, mock_search_agent_cls):
        """Test failed search returns state without recipe to trigger generation"""
        # Setup
        mock_agent = mock_search_agent_cls.return_value
        mock_agent.search.return_value = None
        
        state = {
            "ingredients": ["chicken"], 
            "difficulty": "easy",
            "iteration_count": 0
        }
        
        # Execute
        result = web_search_node(state)
        
        # Verify
        assert result.get("recipe") is None
