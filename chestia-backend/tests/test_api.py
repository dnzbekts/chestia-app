from fastapi.testclient import TestClient
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

# We need to import app, but it doesn't exist yet, so this will fail import
# This is expected for TDD
try:
    from api import app
except ImportError:
    app = None

# If app is None, tests will fail or crash, which is also a "red" state. 
# But to make the test file parseable, we need to handle the import.
# However, for strict TDD, failing at import time is fine.

def test_generate_endpoint_success():
    if not app:
        assert False, "api module not found"
        
    client = TestClient(app)
    
    with patch('api.graph') as mock_graph:
        # Mock return value of graph.invoke
        mock_graph.invoke.return_value = {
            "recipe": {
                "name": "API Pasta",
                "ingredients": ["pasta"],
                "steps": ["cook"],
                "metadata": {}
            },
            "needs_approval": False
        }
        
        response = client.post("/generate", json={"ingredients": ["pasta"]})
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "API Pasta"

def test_generate_endpoint_needs_approval():
    client = TestClient(app)
    with patch('api.graph') as mock_graph:
        mock_graph.invoke.return_value = {
            "recipe": {"name": "Test"},
            "needs_approval": True,
            "error": "Needs extra salt"
        }
        response = client.post("/generate", json={"ingredients": ["salt"]})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "needs_approval"
        assert data["reasoning"] == "Needs extra salt"

def test_feedback_endpoint_approval():
    client = TestClient(app)
    recipe = {"name": "Approved Recipe", "steps": ["step1"]}
    response = client.post("/feedback", json={
        "ingredients": ["egg"],
        "approved": True,
        "recipe": recipe
    })
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_generate_endpoint_invalid_input():
    if not app:
        assert False, "api module not found"
    client = TestClient(app)
    # Missing ingredients field
    response = client.post("/generate", json={})
    assert response.status_code == 422

def test_generate_endpoint_malicious_input():
    client = TestClient(app)
    # Ingredient with special characters not allowed in our Pydantic regex
    response = client.post("/generate", json={"ingredients": ["pasta; drop table recipes--"]})
    assert response.status_code == 422

def test_generate_endpoint_error_masking():
    client = TestClient(app)
    with patch('api.graph') as mock_graph:
        # Simulate a crash/error in the graph
        mock_graph.invoke.side_effect = Exception("Internal SQL Error detail that should be hidden")
        
        response = client.post("/generate", json={"ingredients": ["pasta"]})
        assert response.status_code == 500
        data = response.json()
        assert data["detail"] == "Internal Server Error"
        assert "Internal SQL Error" not in data["detail"]
