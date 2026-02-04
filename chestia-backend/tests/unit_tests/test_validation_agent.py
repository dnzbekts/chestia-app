import pytest
from unittest.mock import MagicMock, patch
from src.workflow.agents.validation_agent import ValidationAgent
from src.infrastructure.localization import i18n

class TestValidationAgent:
    
    @pytest.fixture
    def mock_llm_factory(self):
        with patch("src.workflow.agents.validation_agent.LLMFactory") as mock:
            yield mock

    @pytest.fixture
    def agent(self, mock_llm_factory):
        # Mock the LLM instance created by the factory
        mock_llm = MagicMock()
        mock_llm_factory.create_validation_llm.return_value = mock_llm
        return ValidationAgent()

    def test_validate_success(self, agent):
        """Test validation with sufficient valid ingredients."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.content = '```json\n{"food": ["chicken", "tomato"], "invalid": []}\n```'
        agent.llm.invoke.return_value = mock_response

        # Test
        result = agent.validate(["chicken", "tomato"], "easy")

        # Assertions
        assert result["valid_ingredients"] == ["chicken", "tomato"]
        assert result["invalid_ingredients"] == []
        assert result["normalized_difficulty"] == "easy"
        assert result["error"] is None

    def test_validate_single_ingredient_failure(self, agent):
        """Test validation fails when only 1 valid ingredient is present."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.content = '```json\n{"food": ["chicken"], "invalid": ["stone"]}\n```'
        agent.llm.invoke.return_value = mock_response

        # Test
        result = agent.validate(["chicken", "stone"], "easy")

        # Assertions
        assert len(result["valid_ingredients"]) == 1
        assert result["invalid_ingredients"] == ["stone"]
        assert result["error"] is not None
        assert "Minimum 2 required" in result["error"]

    def test_validate_no_valid_ingredients(self, agent):
        """Test validation fails when no valid ingredients are found."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.content = '```json\n{"food": [], "invalid": ["stone", "paper"]}\n```'
        agent.llm.invoke.return_value = mock_response

        # Test
        result = agent.validate(["stone", "paper"], "hard")

        # Assertions
        assert result["valid_ingredients"] == []
        assert result["invalid_ingredients"] == ["stone", "paper"]
        assert result["error"] == "No valid food ingredients found in the request."

    def test_validate_empty_input(self, agent):
        """Test validation with empty input list."""
        result = agent.validate([], "easy")

        assert result["valid_ingredients"] == []
        assert result["error"] is not None
        # Should match the MIN_INGREDIENTS message key from i18n, but here we just check it exists

    def test_validate_llm_failure_fallback(self, agent):
        """Test fallback behavior when LLM throws an exception."""
        # Setup mock to raise exception
        agent.llm.invoke.side_effect = Exception("LLM Error")

        # Test
        result = agent.validate(["chicken", "tomato"], "medium")

        # Assertions - Fallback assumes all are valid
        assert result["valid_ingredients"] == ["chicken", "tomato"]
        assert result["invalid_ingredients"] == []
        assert result["normalized_difficulty"] == "intermediate"  # "medium" -> "intermediate" check
        assert result["error"] is None
