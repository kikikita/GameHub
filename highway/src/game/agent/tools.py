"""LLM tools used by the game graph."""

import asyncio
import logging
import uuid
from typing import Annotated, Dict

from src.game.agent.llm import create_llm
from src.game.agent.models import (
    Ending,
    EndingCheckResult,
    Scene,
    SceneLLM,
    StoryFrame,
    StoryFrameLLM,
    UserState,
)

from src.game.agent.prompts import ENDING_CHECK_PROMPT, SCENE_PROMPT, STORY_FRAME_PROMPT
from src.game.agent.utils import with_retries
from src.game.images.image_generator import generate_image, get_image_model
from src.game.agent.image_agent import generate_image_prompt
from src.game.agent.npc_agent import maybe_update_npcs

logger = logging.getLogger(__name__)


def _err(msg: str) -> str:
    logger.error(msg)
    return f"{{'error': '{msg}'}}"


async def generate_story_frame(
    setting: Annotated[str, "Game world setting"],
    character: Annotated[Dict[str, str], "Character info"],
    genre: Annotated[str, "Genre"],
    language: Annotated[str, "Output language"],
    visual_style: Annotated[str, "Visual style"],
    npc_characters: Annotated[list[dict], "NPC characters"],
) -> StoryFrame:
    """Create the initial story frame and store it in user state."""
    llm = create_llm().with_structured_output(StoryFrameLLM)
    prompt = STORY_FRAME_PROMPT.format(
        setting=setting,
        character=character,
        genre=genre,
        language=language,
    )
    resp: StoryFrameLLM = await with_retries(lambda: llm.ainvoke(prompt))
    story_frame = StoryFrame(
        lore=resp.lore,
        goal=resp.goal,
        milestones=resp.milestones,
        endings=resp.endings,
        visual_style=visual_style,
        npc_characters=npc_characters,
        setting=setting,
        character=character,
        genre=genre,
        language=language,
    )
    return story_frame


async def generate_initial_scene(
    state: UserState,
) -> Scene:
    """Generate the initial scene for the user."""
    first_scene = await generate_scene("No choice yet", state)
    init_description = (
        f"{first_scene.description}\n"
        "NOTE FOR THE ASSISTANT: YOU MUST GENERATE A NEW IMAGE FOR THE STARTING SCENE. DO NOT DESCRIBE THE PLAYER CHARACTER IN THE IMAGE PROMPT."
    )

    # Run NPC updates in parallel with image prompt + image generation
    npc_task = asyncio.create_task(
        maybe_update_npcs(state, first_scene.description, "No choice yet")
    )
    image_prompt = await generate_image_prompt(state, init_description)
    logger.info(f"Generated initial scene image prompt: {image_prompt}")

    image_path = None
    if image_prompt.change_scene:
        image_path, _ = await generate_image(
            image_prompt.scene_description, state.image_format, get_image_model(state.is_pro)
        )

    # Ensure NPC updates (if any) are applied before returning
    try:
        await npc_task
    except Exception:
        logger.exception("NPC update task failed on initial scene")

    scene_id = str(uuid.uuid4())
    scene = Scene(
        scene_id=scene_id,
        description=first_scene.description,
        choices=first_scene.choices,
        image=image_path,
    )
    state.scenes[scene_id] = scene
    state.last_image_prompt = image_prompt.scene_description
    return scene


async def generate_ending_scene(
    state: UserState,
    ending: Ending,
    choice_text: str,
    last_scene_id: str,
) -> Scene:
    """Generate the ending scene for the user."""
    ending_description = (
        f"Ending ID: {ending.id}\n"
        f"{ending.condition}\n"
        f"{ending.description}\n"
        f"World state:"
        f"{state.story_frame.npc_characters}\n"
        f"{state.story_frame.goal}\n"
        f"{state.story_frame.character}\n"
        f"{state.story_frame.visual_style}\n"
        f"{state.scenes.get(last_scene_id, '')}\n"
        f"Last choice: {choice_text}\n\n"
        "NOTE FOR THE ASSISTANT: YOU MUST GENERATE A NEW IMAGE FOR THE ENDING SCENE"
    )
    image_prompt = await generate_image_prompt(state, ending_description)
    logger.info(f"Generated ending scene image prompt: {image_prompt}")

    if image_prompt.change_scene:
        image_path, _ = await generate_image(
            image_prompt.scene_description, state.image_format, get_image_model(state.is_pro)
        )

    scene_id = str(uuid.uuid4())
    scene = Scene(
        scene_id=scene_id,
        description=ending.description,
        choices=[],
        image=image_path,
    )
    state.scenes[scene_id] = scene
    state.last_image_prompt = image_prompt.scene_description
    return scene


async def generate_scene(
    last_choice: Annotated[str, "Last user choice"],
    state: UserState,
) -> SceneLLM:
    """Generate a new scene based on the current user state."""
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
        language=state.language,
        npc_characters="\n".join(
            f"{c.char_name}: {c.visual_description}"
            for c in state.story_frame.npc_characters
        ),
        main_character=state.story_frame.character,
    )
    resp: SceneLLM = await with_retries(lambda: llm.ainvoke(prompt))
    return resp


async def generate_scene_step(last_choice: str, state: UserState) -> Scene:
    """Generate a new scene based on the current user state."""
    scene = await generate_scene(last_choice, state)

    logger.info(f"Generated scene step: {scene}")

    # Kick off NPC update in parallel with image prompt + image generation
    npc_task = asyncio.create_task(
        maybe_update_npcs(state, scene.description, last_choice)
    )
    image_prompt = await generate_image_prompt(state, scene.description)
    logger.info(f"Generated scene step image prompt: {image_prompt}")

    image_path = None
    if image_prompt.change_scene:
        image_path, _ = await generate_image(
            image_prompt.scene_description, state.image_format, get_image_model(state.is_pro)
        )

    # Ensure NPC update is applied before returning so persistence sees it
    try:
        await npc_task
    except Exception:
        logger.exception("NPC update task failed on scene step")

    scene_id = str(uuid.uuid4())
    scene = Scene(
        scene_id=scene_id,
        description=scene.description,
        choices=scene.choices,
        image=image_path,
    )
    state.scenes[scene_id] = scene
    state.last_image_prompt = image_prompt.scene_description
    return scene


async def check_ending(
    state: UserState,
) -> EndingCheckResult:
    """Check whether an ending has been reached."""
    if not state.story_frame:
        return _err("No story frame")
    llm = create_llm().with_structured_output(EndingCheckResult)
    history = "; ".join(f"{c.scene_id}:{c.choice_text}" for c in state.user_choices)
    prompt = ENDING_CHECK_PROMPT.format(
        history=history,
        language=state.language,
        endings=",".join(f"{e.id}:{e.condition}" for e in state.story_frame.endings),
    )
    resp: EndingCheckResult = await with_retries(lambda: llm.ainvoke(prompt))
    return resp
