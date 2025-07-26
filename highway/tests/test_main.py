import os
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("TG_BOT_TOKEN", "test")
os.environ.setdefault("GRADIO_APP_URL", "http://test")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
from src.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health-check")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
