import os
import sys
import uuid
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import httpx

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("TG_BOT_TOKEN", "test")
os.environ.setdefault("GRADIO_APP_URL", "http://test")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

from sqlalchemy.dialects import postgresql
from sqlalchemy import JSON
postgresql.JSONB = JSON

from src.main import app
from src.core.database import get_session
from src.models import Base
from src.auth.tg_auth import authenticated_user


@pytest_asyncio.fixture()
async def client():
    engine = create_async_engine(os.environ["DATABASE_URL"], future=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def override_get_session():
        async with async_session() as session:
            yield session

    async def override_auth():
        return {"user_id": 1}

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[authenticated_user] = override_auth

    transport = httpx.ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_full_flow(client: AsyncClient):
    resp = await client.post("/api/v1/auth/register", json={"tg_id": 1, "username": "tester"})
    assert resp.status_code == 201

    resp = await client.get("/api/v1/users/me")
    assert resp.status_code == 200
    assert resp.json()["tg_id"] == 1

    t_payload = {
        "setting_desc": "A dark cave",
        "char_name": "Hero",
        "char_age": "30",
        "char_background": "Brave",
        "char_personality": "Bold",
        "genre": "Fantasy",
    }
    resp = await client.post("/api/v1/templates", json=t_payload)
    assert resp.status_code == 201
    tid = resp.json()["id"]

    resp = await client.get("/api/v1/templates")
    assert resp.status_code == 200

    resp = await client.get(f"/api/v1/templates/{tid}")
    assert resp.status_code == 200

    resp = await client.post(f"/api/v1/templates/{tid}/share")
    assert resp.status_code == 200
    share_code = resp.json()["share_code"]

    resp = await client.get(f"/api/v1/templates/shared/{share_code}")
    assert resp.status_code == 200

    resp = await client.post("/api/v1/sessions", json={"template_id": tid})
    assert resp.status_code == 201
    session_id = resp.json()["id"]

    resp = await client.get(f"/api/v1/sessions/{session_id}")
    assert resp.status_code == 200

    resp = await client.post(f"/api/v1/sessions/{session_id}/scenes")
    assert resp.status_code == 201
    scene_id = resp.json()["id"]

    resp = await client.get(f"/api/v1/sessions/{session_id}/scenes/{scene_id}")
    assert resp.status_code == 200

    resp = await client.post(f"/api/v1/sessions/{session_id}/choice", json={"choice_text": "go"})
    assert resp.status_code == 201

    resp = await client.get(f"/api/v1/sessions/{session_id}/history")
    assert resp.status_code == 200

    resp = await client.put(
        f"/api/v1/sessions/{session_id}/scenes/{scene_id}",
        json={"id": scene_id, "description": "Updated", "image_url": None, "choices_json": None},
    )
    assert resp.status_code == 200


    resp = await client.get("/api/v1/plans")
    assert resp.status_code == 200

    resp = await client.post("/api/v1/subscribe")
    assert resp.status_code == 200

    resp = await client.get("/api/v1/subscription/status")
    assert resp.status_code == 200
