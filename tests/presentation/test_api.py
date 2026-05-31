from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    """Verifies that the presentation API serves the /health endpoint correctly."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
