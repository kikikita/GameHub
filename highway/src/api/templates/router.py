from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.tg_auth import authenticated_user
from src.core.database import get_session
import json
import uuid
from .schemas import TemplateCreate, TemplateOut, TemplateShareOut
from .template_service import (
    create_template,
    get_shared_template,
    get_template,
    list_templates,
    share_template,
)

router = APIRouter(prefix="/api/v1/templates", tags=["templates"])


@router.post("", response_model=TemplateOut, status_code=status.HTTP_201_CREATED)
async def create_my_template(payload: TemplateCreate, user_data: dict = Depends(authenticated_user), db: AsyncSession = Depends(get_session)):
    user_id = uuid.UUID(str(user_data.get("user_id") or user_data.get("id") or json.loads(user_data.get("user", "{}")).get("id")))
    template = await create_template(db, user_id, payload.model_dump())
    return template


@router.get("", response_model=list[TemplateOut])
async def list_my_templates(user_data: dict = Depends(authenticated_user), db: AsyncSession = Depends(get_session)):
    user_id = uuid.UUID(str(user_data.get("user_id") or user_data.get("id") or json.loads(user_data.get("user", "{}")).get("id")))
    templates = await list_templates(db, user_id)
    return templates


@router.get("/{template_id}", response_model=TemplateOut)
async def read_template(template_id: str, user_data: dict = Depends(authenticated_user), db: AsyncSession = Depends(get_session)):
    user_id = uuid.UUID(str(user_data.get("user_id") or user_data.get("id") or json.loads(user_data.get("user", "{}")).get("id")))
    template = await get_template(db, user_id, uuid.UUID(template_id))
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return template


@router.post("/{template_id}/share", response_model=TemplateShareOut)
async def share_my_template(template_id: str, user_data: dict = Depends(authenticated_user), db: AsyncSession = Depends(get_session)):
    user_id = uuid.UUID(str(user_data.get("user_id") or user_data.get("id") or json.loads(user_data.get("user", "{}")).get("id")))
    template = await share_template(db, user_id, uuid.UUID(template_id))
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return TemplateShareOut(id=str(template.id), share_code=str(template.id))


@router.get("/shared/{code}", response_model=TemplateOut)
async def get_shared(code: str, db: AsyncSession = Depends(get_session)):
    template = await get_shared_template(db, code)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return template

