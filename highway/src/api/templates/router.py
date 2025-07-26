from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.tg_auth import authenticated_user
from src.core.database import get_session
from .schemas import TemplateCreate, TemplateOut, TemplateShareOut
from .template_service import (
    create_template,
    get_shared_template,
    get_template,
    list_templates,
    share_template,
)
from src.api.utils import resolve_user_id
import uuid

router = APIRouter(prefix="/api/v1/templates", tags=["templates"])


@router.post("", response_model=TemplateOut, status_code=status.HTTP_201_CREATED)
async def create_my_template(payload: TemplateCreate, user_data: dict = Depends(authenticated_user), db: AsyncSession = Depends(get_session)):
    user_id = await resolve_user_id(db, user_data)
    template = await create_template(db, user_id, payload.model_dump())
    return TemplateOut(
        id=str(template.id),
        setting_desc=template.setting_desc,
        char_name=template.char_name,
        char_age=template.char_age,
        char_background=template.char_background,
        char_personality=template.char_personality,
        genre=template.genre,
        is_public=template.is_public,
        created_at=template.created_at,
    )


@router.get("", response_model=list[TemplateOut])
async def list_my_templates(user_data: dict = Depends(authenticated_user), db: AsyncSession = Depends(get_session)):
    user_id = await resolve_user_id(db, user_data)
    templates = await list_templates(db, user_id)
    return [
        TemplateOut(
            id=str(t.id),
            setting_desc=t.setting_desc,
            char_name=t.char_name,
            char_age=t.char_age,
            char_background=t.char_background,
            char_personality=t.char_personality,
            genre=t.genre,
            is_public=t.is_public,
            created_at=t.created_at,
        )
        for t in templates
    ]


@router.get("/{template_id}", response_model=TemplateOut)
async def read_template(template_id: str, user_data: dict = Depends(authenticated_user), db: AsyncSession = Depends(get_session)):
    user_id = await resolve_user_id(db, user_data)
    template = await get_template(db, user_id, uuid.UUID(template_id))
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return TemplateOut(
        id=str(template.id),
        setting_desc=template.setting_desc,
        char_name=template.char_name,
        char_age=template.char_age,
        char_background=template.char_background,
        char_personality=template.char_personality,
        genre=template.genre,
        is_public=template.is_public,
        created_at=template.created_at,
    )


@router.post("/{template_id}/share", response_model=TemplateShareOut)
async def share_my_template(template_id: str, user_data: dict = Depends(authenticated_user), db: AsyncSession = Depends(get_session)):
    user_id = await resolve_user_id(db, user_data)
    template = await share_template(db, user_id, uuid.UUID(template_id))
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return TemplateShareOut(id=str(template.id), share_code=str(template.id))


@router.get("/shared/{code}", response_model=TemplateOut)
async def get_shared(code: str, db: AsyncSession = Depends(get_session)):
    template = await get_shared_template(db, code)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return TemplateOut(
        id=str(template.id),
        setting_desc=template.setting_desc,
        char_name=template.char_name,
        char_age=template.char_age,
        char_background=template.char_background,
        char_personality=template.char_personality,
        genre=template.genre,
        is_public=template.is_public,
        created_at=template.created_at,
    )
