import uuid
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.scene import Scene
from src.models.choice import Choice
from src.models.game_session import GameSession
from src.models.story import Story
from src.game.agent.runner import process_step, SceneResponse
from src.game.agent.redis_state import get_user_state, set_user_state
from src.game.agent.models import StoryFrame, UserChoice, UserState
from src.game.agent.tools import generate_story_frame, generate_initial_scene
import logging

logger = logging.getLogger(__name__)
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
    story: Story | None = None,
) -> Scene:
    user_hash = str(session.id)
    state = await get_user_state(user_hash)
    if not state.story_frame:
        if session.story_frame:
            sf_data = dict(session.story_frame)
            if (
                ("setting" not in sf_data or "character" not in sf_data or "genre" not in sf_data)
                and session.story
            ):
                await db.refresh(session.story, ["world"])
                sf_data.setdefault("setting", session.story.world.world_desc)
                sf_data.setdefault("character", session.story.character or {})
                sf_data.setdefault("genre", session.story.genre)
            state.story_frame = StoryFrame(**sf_data)
        elif session.story and session.story.story_frame:
            await db.refresh(session.story, ["world"])
            sf_data = dict(session.story.story_frame)
            sf_data.setdefault("setting", session.story.world.world_desc)
            sf_data.setdefault("character", session.story.character or {})
            sf_data.setdefault("genre", session.story.genre)
            state.story_frame = StoryFrame(**sf_data)

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

    order_num = await _next_order(db, session.id)
    if order_num == 1:
        if story is None:
            story = session.story
            if story is not None:
                await db.refresh(story, ["world"])
        if not story:
            raise ValueError("Story not found for session")
        world = story.world
        if not state.story_frame:
            story_frame = await generate_story_frame(
                setting=world.world_desc,
                character=story.character or {},
                genre=story.genre,
            )
            state.story_frame = story_frame
        else:
            story_frame = state.story_frame
        logger.info(f"Possible endings: {story_frame.endings}")
        initial_scene = await generate_initial_scene(state)
        result = SceneResponse(scene=initial_scene, game_over=False)
    else:
        logger.info("[Runner] Step %s for user %s", state.current_scene_id, user_hash)
        result = await process_step(state, choice_text)

    if order_num == 1 and not session.story_frame:
        if state.story_frame:
            session.story_frame = state.story_frame.model_dump()
            db.add(session)
            await db.commit()
            await db.refresh(session)

    if result.game_over:
        ending = result.ending
        description = ending.description
        image_path = result.scene.image
        choices_json = None
        session.is_finished = True
        session.ended_at = datetime.utcnow()
        db.add(session)
    else:
        scene_data = result.scene
        description = scene_data.description
        image_path = scene_data.image
        choices_json = {"choices": [c.model_dump() for c in scene_data.choices]}

    scene = Scene(
        session_id=session.id,
        order_num=order_num,
        description=description,
        generated_choices=choices_json,
        image_path=image_path,
    )
    await set_user_state(user_hash, state)
    db.add(scene)
    await db.flush()

    if choice_text:
        db.add(Choice(scene_id=scene.id, choice_text=choice_text))

    await db.commit()
    await db.refresh(scene)
    return scene
