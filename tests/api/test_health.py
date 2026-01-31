"""Tests for health check endpoint."""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test health check endpoint returns OK status."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "service" in data


def test_health_check_structure(client: TestClient):
    """Test health check response structure."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "status" in data
    assert "service" in data
    assert data["status"] == "ok"
