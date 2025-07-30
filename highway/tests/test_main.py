import os, sys, pathlib, pytest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'src'))
from fastapi.testclient import TestClient
try:
    from src.main import app
except Exception:
    app = None


def test_health_check():
    if app is None:
        pytest.skip('src.main not available')
    client = TestClient(app)
    response = client.get('/health-check')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}
