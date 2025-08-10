"""Entry point for executing a graph step."""

import logging
from typing import Literal, Optional, Union

import datetime
import asyncio
from pydantic import BaseModel
from src.game.agent.models import (
    Ending,
    EndingCheckResult,
    Scene,
    UserState,
    UserChoice,
)
from src.game.agent.tools import (
    check_ending,
    generate_ending_scene,
    generate_scene_step,
)

logger = logging.getLogger(__name__)


class EndingResponse(BaseModel):
    ending: Ending
    scene: Scene
    game_over: Literal[True]


class SceneResponse(BaseModel):
    scene: Scene
    game_over: Literal[False]


ProcessStepResponse = Union[EndingResponse, SceneResponse]


async def process_step(
    state: UserState,
    choice_text: str,
) -> ProcessStepResponse:
    """Run one interaction step through the graph."""

    last_scene_id = state.current_scene_id
    state.user_choices.append(
        UserChoice(
            scene_id=last_scene_id,
            choice_text=choice_text,
            timestamp=datetime.datetime.utcnow().isoformat(),
        )
    )

    ending_task = check_ending(state)
    next_scene_task = generate_scene_step(choice_text, state)
    maybe_ending, next_scene = await asyncio.gather(ending_task, next_scene_task)

    if maybe_ending is None:
        logger.error("check_ending returned None; continuing the game")
        maybe_ending = EndingCheckResult(ending_reached=False, ending=None)
        
    if (
        maybe_ending.ending is not None
        and maybe_ending.ending.type == "good"
        and len(state.user_choices) < 15
    ):
        logger.info(f"Ending is good but the game is too short; continuing the game")
        maybe_ending = EndingCheckResult(ending_reached=False, ending=None)

    if maybe_ending.ending_reached and maybe_ending.ending is not None:
        state.ending = maybe_ending.ending
        scene = await generate_ending_scene(
            state, maybe_ending.ending, choice_text, last_scene_id
        )

        response = EndingResponse(
            scene=scene,
            game_over=True,
            ending=maybe_ending.ending,
        )
    else:
        if maybe_ending.ending_reached and maybe_ending.ending is None:
            logger.error(
                "Ending was reported as reached but no ending data was provided; continuing the game"
            )
        state.current_scene_id = next_scene.scene_id
        response = SceneResponse(
            scene=next_scene,
            game_over=False,
        )

    return response
