import pytest
import sqlite3
import os
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from src.main import app

@pytest.fixture
def mock_llm():
    """Fixture to mock LLM responses."""
    with patch("src.infrastructure.llm_factory.LLMFactory.create_llm") as mock:
        llm_instance = MagicMock()
        mock.return_value = llm_instance
        yield llm_instance

@pytest.fixture
def test_db():
    """Fixture to provide an in-memory database connection with sqlite-vec."""
    import sqlite_vec
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    
    # Import here to avoid issues with database initialization
    from src.infrastructure.database import init_db
    init_db(conn)
    yield conn
    conn.close()

@pytest.fixture
def api_client():
    """Fixture for FastAPI TestClient."""
    return TestClient(app)

@pytest.fixture
def sample_generate_payload():
    """Sample payload for /generate endpoint."""
    return {
        "ingredients": ["chicken", "tomato", "onion"],
        "difficulty": "easy",
        "lang": "en"
    }

@pytest.fixture
def sample_recipe_data():
    """Sample structured recipe data."""
    return {
        "name": "Test Recipe",
        "ingredients": ["item1", "item2"],
        "steps": ["step 1", "step 2"],
        "metadata": {"time": "15min", "difficulty": "easy"}
    }
