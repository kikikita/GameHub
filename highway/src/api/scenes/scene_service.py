import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.scene import Scene
from src.models.choice import Choice
from src.models.game_session import GameSession
from src.game.agent.runner import process_step
from src.game.agent.redis_state import get_user_state, set_user_state
from src.game.agent.models import StoryFrame, UserChoice, UserState


async def _next_order(db: AsyncSession, session_id: uuid.UUID) -> int:
    res = await db.execute(
        select(func.max(Scene.order_num)).where(Scene.session_id == session_id)
    )
    max_order = res.scalar_one()
    return 1 if max_order is None else max_order + 1


async def create_and_store_scene(
    db: AsyncSession,
    session: GameSession,
    choice_text: str | None,
) -> Scene:
    user_hash = str(session.id)
    state = await get_user_state(user_hash)
    if not state.story_frame:
        if session.story_frame:
            state.story_frame = StoryFrame(**session.story_frame)
        elif session.template and session.template.story_frame:
            state.story_frame = StoryFrame(**session.template.story_frame)
        if state.story_frame:
            await set_user_state(user_hash, state)

    if not state.user_choices:
        res = await db.execute(
            select(Scene, Choice)
            .join(Choice, isouter=True)
            .where(Scene.session_id == session.id)
            .order_by(Scene.order_num)
        )
        rows = res.all()
        for sc, ch in rows:
            if ch:
                state.user_choices.append(
                    UserChoice(scene_id=str(sc.id), choice_text=ch.choice_text)
                )
        if rows:
            state.current_scene_id = str(rows[-1][0].id)
        await set_user_state(user_hash, state)

    order_num = await _next_order(db, session.id)
    if order_num == 1:
        template = session.template
        if not template:
            raise ValueError("Template not found for session")
        result = await process_step(
            user_hash=user_hash,
            step="start",
            setting=template.setting_desc or "",
            character={
                "name": template.char_name or "",
                "age": template.char_age or "",
                "background": template.char_background or "",
                "personality": template.char_personality or "",
            },
            genre=template.genre or "",
        )
    else:
        result = await process_step(
            user_hash=user_hash,
            step="choose",
            choice_text=choice_text or "",
        )

    if order_num == 1 and not session.story_frame:
        state = await get_user_state(user_hash)
        if state.story_frame:
            session.story_frame = state.story_frame.model_dump()
            db.add(session)
            await db.commit()
            await db.refresh(session)

    if result.get("game_over"):
        ending = result["ending"]
        description = (ending.get("description") or ending.get("condition", ""))
        image_path = result.get("image")
        choices_json = None
    else:
        scene_data = result["scene"]
        description = scene_data.get("description")
        image_path = scene_data.get("image")
        choices_json = {"choices": scene_data.get("choices", [])}

    scene = Scene(
        session_id=session.id,
        order_num=order_num,
        description=description,
        generated_choices=choices_json,
        image_path=image_path,
    )
    db.add(scene)
    await db.flush()

    if choice_text:
        db.add(Choice(scene_id=scene.id, choice_text=choice_text))

    await db.commit()
    await db.refresh(scene)
    return scene
