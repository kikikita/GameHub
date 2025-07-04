"""LLM tools used by the game graph."""

import logging
import uuid
from typing import Annotated, Dict

from langchain_core.tools import tool

from agent.llm import create_llm
from agent.models import (
    EndingCheckResult,
    Scene,
    SceneChoice,
    SceneLLM,
    StoryFrame,
    StoryFrameLLM,
    UserChoice,
)
from agent.prompts import ENDING_CHECK_PROMPT, SCENE_PROMPT, STORY_FRAME_PROMPT
from agent.redis_state import get_user_state, set_user_state
from agent.utils import with_retries
from images.image_generator import modify_image, generate_image
from agent.image_agent import ChangeScene

logger = logging.getLogger(__name__)


def _err(msg: str) -> str:
    logger.error(msg)
    return f"{{'error': '{msg}'}}"


@tool
async def generate_story_frame(
    user_hash: Annotated[str, "User session ID"],
    setting: Annotated[str, "Game world setting"],
    character: Annotated[Dict[str, str], "Character info"],
    genre: Annotated[str, "Genre"],
) -> Annotated[Dict, "Generated story frame"]:
    """Create the initial story frame and store it in user state."""
    llm = create_llm().with_structured_output(StoryFrameLLM)
    prompt = STORY_FRAME_PROMPT.format(
        setting=setting,
        character=character,
        genre=genre,
    )
    resp: StoryFrameLLM = await with_retries(lambda: llm.ainvoke(prompt))
    story_frame = StoryFrame(
        lore=resp.lore,
        goal=resp.goal,
        milestones=resp.milestones,
        endings=resp.endings,
        setting=setting,
        character=character,
        genre=genre,
    )
    state = await get_user_state(user_hash)
    state.story_frame = story_frame
    await set_user_state(user_hash, state)
    return story_frame.dict()


@tool
async def generate_scene(
    user_hash: Annotated[str, "User session ID"],
    last_choice: Annotated[str, "Last user choice"],
) -> Annotated[Dict, "Generated scene"]:
    """Generate a new scene based on the current user state."""
    state = await get_user_state(user_hash)
    if not state.story_frame:
        return _err("Story frame not initialized")
    llm = create_llm().with_structured_output(SceneLLM)
    prompt = SCENE_PROMPT.format(
        lore=state.story_frame.lore,
        goal=state.story_frame.goal,
        milestones=",".join(m.id for m in state.story_frame.milestones),
        endings=",".join(e.id for e in state.story_frame.endings),
        history="; ".join(f"{c.scene_id}:{c.choice_text}" for c in state.user_choices),
        last_choice=last_choice,
    )
    resp: SceneLLM = await with_retries(lambda: llm.ainvoke(prompt))
    if len(resp.choices) < 2:
        resp = await with_retries(
            lambda: llm.ainvoke(prompt + "\nThe scene must contain exactly two choices.")
        )
    scene_id = str(uuid.uuid4())
    choices = [
        SceneChoice(**ch.model_dump())
        if hasattr(ch, "model_dump")
        else SceneChoice(**ch)
        for ch in resp.choices[:2]
    ]
    scene = Scene(
        scene_id=scene_id,
        description=resp.description,
        choices=choices,
        image=None,
        music=None,
    )
    state.current_scene_id = scene_id
    state.scenes[scene_id] = scene
    await set_user_state(user_hash, state)
    return scene.dict()


@tool
async def generate_scene_image(
    user_hash: Annotated[str, "User session ID"],
    scene_id: Annotated[str, "Scene ID"],
    change_scene: Annotated[ChangeScene, "Prompt for image generation"],
    current_image: Annotated[str, "Current image"] | None = None,
) -> Annotated[str, "Path to generated image"]:
    """Generate an image for a scene and save the path in the state."""
    try:
        image_path = current_image
        if change_scene.change_scene == "change_completely" or change_scene.change_scene == "modify":
            image_path, _ = await (
                generate_image(change_scene.scene_description)
                if current_image is None
                # for now always modify the image to avoid the generating an update in a completely wrong style
                else modify_image(current_image, change_scene.scene_description)
            )
        state = await get_user_state(user_hash)
        if scene_id in state.scenes:
            state.scenes[scene_id].image = image_path
        await set_user_state(user_hash, state)
        return image_path
    except Exception as exc:  # noqa: BLE001
        return _err(str(exc))


@tool
async def update_state_with_choice(
    user_hash: Annotated[str, "User session ID"],
    scene_id: Annotated[str, "Scene ID"],
    choice_text: Annotated[str, "Chosen option"],
) -> Annotated[Dict, "Updated state"]:
    """Record the player's choice in the state."""
    import datetime

    state = await get_user_state(user_hash)
    state.user_choices.append(
        UserChoice(
            scene_id=scene_id,
            choice_text=choice_text,
            timestamp=datetime.datetime.utcnow().isoformat(),
        )
    )
    await set_user_state(user_hash, state)
    return state.dict()


@tool
async def check_ending(
    user_hash: Annotated[str, "User session ID"],
) -> Annotated[Dict, "Ending check result"]:
    """Check whether an ending has been reached."""
    state = await get_user_state(user_hash)
    if not state.story_frame:
        return _err("No story frame")
    llm = create_llm().with_structured_output(EndingCheckResult)
    history = "; ".join(f"{c.scene_id}:{c.choice_text}" for c in state.user_choices)
    prompt = ENDING_CHECK_PROMPT.format(
        history=history,
        endings=",".join(f"{e.id}:{e.condition}" for e in state.story_frame.endings),
    )
    resp: EndingCheckResult = await with_retries(lambda: llm.ainvoke(prompt))
    if resp.ending_reached and resp.ending:
        state.ending = resp.ending
        await set_user_state(user_hash, state)
        return {"ending_reached": True, "ending": resp.ending.dict()}
    return {"ending_reached": False}
