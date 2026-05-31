import pytest
from fastapi.testclient import TestClient

from isb.presentation.api import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    """Fixture supplying a FastAPI TestClient for routing assertions."""
    return TestClient(app)
