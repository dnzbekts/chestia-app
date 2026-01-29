import pytest
from src.infrastructure.localization.i18n import get_message, MIN_INGREDIENTS

def test_get_message_en():
    """Test English message retrieval."""
    msg = get_message(MIN_INGREDIENTS, "en")
    assert "At least one non-default ingredient" in msg

def test_get_message_tr():
    """Test Turkish message retrieval."""
    msg = get_message(MIN_INGREDIENTS, "tr")
    assert "En az bir adet default olmayan" in msg

def test_get_message_fallback_lang():
    """Test fallback to English for unknown language."""
    msg = get_message(MIN_INGREDIENTS, "fr")
    assert "At least one non-default ingredient" in msg

def test_get_message_missing_key():
    """Test behavior with missing key."""
    msg = get_message("NON_EXISTENT_KEY")
    assert "NON_EXISTENT_KEY" in msg
