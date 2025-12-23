from fastapi.testclient import TestClient
from src.main import app
from src.core.config import settings
from unittest.mock import patch

def test_generate_story_no_auth(client):
    """
    Test that request without API key fails when Auth is enabled.
    """
    # Simulate API_KEY being set
    with patch("src.api.deps.settings.API_KEY", "test-secret"):
        payload = {
            "keywords": ["ninja"],
            "genre": "fantasy",
            "tone": "humorous"
        }
        response = client.post(f"{settings.API_V1_STR}/generate", json=payload)
        assert response.status_code == 401
        assert response.json()["detail"] == "Could not validate credentials"

def test_generate_story_invalid_auth(client):
    """
    Test that request with wrong API key fails.
    """
    with patch("src.api.deps.settings.API_KEY", "test-secret"):
        payload = {
            "keywords": ["ninja"],
            "genre": "fantasy",
        }
        headers = {"X-API-Key": "wrong-secret"}
        response = client.post(f"{settings.API_V1_STR}/generate", json=payload, headers=headers)
        assert response.status_code == 401

def test_generate_story_valid_auth(client):
    """
    Test that request with correct API key succeeds.
    """
    with patch("src.api.deps.settings.API_KEY", "test-secret"):
        payload = {
            "keywords": ["ninja"],
            "genre": "fantasy",
            "tone": "humorous"
        }
        headers = {"X-API-Key": "test-secret"}
        response = client.post(f"{settings.API_V1_STR}/generate", json=payload, headers=headers)
        assert response.status_code == 200
        assert "title" in response.json()
