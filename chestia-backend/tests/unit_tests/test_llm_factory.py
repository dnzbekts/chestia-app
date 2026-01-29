import pytest
import os
from unittest.mock import patch
from src.infrastructure.llm_factory import LLMFactory

def test_validate_api_key_valid():
    """Test with a valid-looking key."""
    key = "AIza" + "x" * 20
    assert LLMFactory._validate_api_key(key) == key

@pytest.mark.parametrize("key", [
    None,
    "",
    "YOUR_KEY_HERE",
    "REPLACE_ME",
    "not-a-google-key",
    "AIza-too-short"
])
def test_validate_api_key_invalid(key):
    """Test with various invalid keys."""
    with pytest.raises(RuntimeError):
        LLMFactory._validate_api_key(key)

def test_create_llm_with_custom_temp():
    """Test LLM creation with custom parameters."""
    with patch("src.infrastructure.llm_factory.ChatGoogleGenerativeAI") as mock_chat:
        LLMFactory.create_llm(temperature=0.9, api_key="AIza" + "x" * 20)
        mock_chat.assert_called_with(
            model="gemini-2.0-flash",
            google_api_key="AIza" + "x" * 20,
            temperature=0.9
        )

def test_create_recipe_llm():
    """Test recipe-specific LLM creation."""
    with patch("src.infrastructure.llm_factory.LLMFactory.create_llm") as mock_create:
        LLMFactory.create_recipe_llm()
        mock_create.assert_called_with(model="gemini-2.0-flash", temperature=0.7)

def test_create_review_llm():
    """Test review-specific LLM creation."""
    with patch("src.infrastructure.llm_factory.LLMFactory.create_llm") as mock_create:
        LLMFactory.create_review_llm()
        mock_create.assert_called_with(model="gemini-2.0-flash", temperature=0)
