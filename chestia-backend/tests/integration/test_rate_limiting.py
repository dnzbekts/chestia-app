import pytest
from fastapi.testclient import TestClient
from src.main import app
import time

client = TestClient(app)

def test_rate_limiting_generate():
    """Verify rate limiting on /generate endpoint."""
    # The limit is 5/minute. We try 6 times.
    for i in range(5):
        response = client.post("/generate", json={
            "ingredients": ["egg", "flour", "milk"],
            "difficulty": "easy",
            "lang": "en"
        })
        # If it returns 500 or 422 that's fine for testing the limiter, 
        # but we expect it to eventually return 429.
        # Note: If the backend actually generates a recipe, it might be slow.
    
    # 6th request should be rate limited
    response = client.post("/generate", json={
        "ingredients": ["egg", "flour", "milk"],
        "difficulty": "easy"
    })
    # SlowAPI returns 429 for rate limit exceeded with a JSON error message
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.text
