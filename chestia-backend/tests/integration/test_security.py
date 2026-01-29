import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_security_headers():
    """Verify that standard security headers are present in responses."""
    response = client.get("/api/openapi.json")
    assert response.status_code == 200
    
    # Headers to check
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert "Strict-Transport-Security" in response.headers
    assert "Content-Security-Policy" in response.headers
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"

def test_cors_headers():
    """Verify CORS headers (basic check)."""
    response = client.options("/generate", headers={
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST"
    })
    assert response.status_code == 200
    # When allow_origins=["*"], FastAPI returns the requested origin in the response header
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
