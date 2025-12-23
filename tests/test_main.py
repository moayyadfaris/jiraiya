from src.core.config import settings

def test_health_check(client):
    response = client.get(f"{settings.API_V1_STR}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Jiraiya Service 🐸"}

def test_generate_story_mock_mode(client):
    """
    Test generation without API key (Mock Mode).
    """
    payload = {
        "keywords": ["ninja", "toad"],
        "genre": "fantasy",
        "tone": "humorous"
    }
    response = client.post(f"{settings.API_V1_STR}/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "title" in data
    assert "content" in data
    assert "keywords_used" in data
    assert "Min length requested" in data["content"] or "ninja" in data["content"]

def test_generate_story_validation_empty_keywords(client):
    """
    Test that empty keywords list fails validation.
    """
    payload = {
        "keywords": [],
        "genre": "fantasy",
        "tone": "humorous"
    }
    response = client.post(f"{settings.API_V1_STR}/generate", json=payload)
    assert response.status_code == 422
    assert "validation" in response.text.lower() or "field required" in response.text.lower()

def test_generate_story_validation_invalid_tone(client):
    """
    Test that invalid tone fails validation.
    """
    payload = {
        "keywords": ["ninja"],
        "genre": "fantasy",
        "tone": "invalid_tone_xyz"
    }
    response = client.post(f"{settings.API_V1_STR}/generate", json=payload)
    assert response.status_code == 422
    assert "tone" in response.text.lower() or "validation" in response.text.lower()

def test_generate_story_validation_length_range(client):
    """
    Test that min_length > max_length fails validation.
    """
    payload = {
        "keywords": ["ninja"],
        "genre": "fantasy",
        "min_length": 1000,
        "max_length": 500
    }
    response = client.post(f"{settings.API_V1_STR}/generate", json=payload)
    assert response.status_code == 422

def test_generate_story_validation_max_length_bounds(client):
    """
    Test that max_length outside bounds fails validation.
    """
    payload = {
        "keywords": ["ninja"],
        "genre": "fantasy",
        "max_length": 5000  # Exceeds max of 2000
    }
    response = client.post(f"{settings.API_V1_STR}/generate", json=payload)
    assert response.status_code == 422

