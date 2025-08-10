"""Agent for detecting and applying NPC updates from scene text."""

import logging
from typing import List, Literal, Optional, Tuple

from pydantic import BaseModel, Field

from src.game.agent.llm import create_light_llm
from src.game.agent.models import NPCCharacter, UserState
from src.game.agent.prompts import NPC_UPDATE_PROMPT
from src.game.agent.utils import with_retries

logger = logging.getLogger(__name__)


class NPCUpdateAction(BaseModel):
    """Single update operation for an NPC character."""

    operation: Literal["add", "update", "remove"] = Field(
        description="Type of change to apply to the NPC list"
    )
    char_name: str = Field(description="Character name to identify target")

    # For add or update operations. For update include only changed fields.
    char_age: Optional[str] = Field(description="Age of the character")
    char_background: Optional[str] = Field(description="Background of the character")
    char_personality: Optional[str] = Field(description="Stable personality in 3–7 adjectives or short noun phrases, comma-separated. No sentences. No references to the player or momentary states.")
    visual_description: Optional[str] = Field(description="""immutable visual identity ONLY. Include physical traits, distinctive features, species, build, clothing/outfit that persist beyond a single moment. EXCLUDE transient actions, emotions, poses, camera directions, lighting, time-bound states, or references to the player (e.g., "looks at you", "now", "today"). Use 10 - 25 words, comma-separated attributes, no sentences, no second-person pronouns.""")


class NPCUpdates(BaseModel):
    """Batch of NPC update actions decided by the LLM."""

    actions: List[NPCUpdateAction] = Field(default_factory=list)


def _npc_list_to_prompt(npcs: List[NPCCharacter]) -> str:
    if not npcs:
        return "(none)"
    return "\n".join(
        f"{c.char_name} | age:{c.char_age} | persona:{c.char_personality} | bg:{c.char_background} | visual:{c.visual_description}"
        for c in npcs
    )


async def propose_npc_updates(state: UserState, scene_description: str, last_choice: str = "") -> NPCUpdates:
    """Ask the LLM to propose NPC updates based on latest scene and existing list."""
    llm = create_light_llm(temperature=0.1).with_structured_output(NPCUpdates)

    npc_context = _npc_list_to_prompt(state.story_frame.npc_characters if state.story_frame else [])

    sf = state.story_frame
    prompt = NPC_UPDATE_PROMPT.format(
        lore=sf.lore if sf else "",
        goal=sf.goal if sf else "",
        milestones=",".join(m.id for m in (sf.milestones if sf else [])),
        endings=",".join(e.id for e in (sf.endings if sf else [])),
        npc_characters=npc_context,
        scene_description=scene_description,
        last_choice=last_choice or "No choice yet",
        main_character=state.story_frame.character,
    )

    response: NPCUpdates = await with_retries(lambda: llm.ainvoke(prompt))
    return response


def _apply_action(existing: List[NPCCharacter], action: NPCUpdateAction) -> Tuple[List[NPCCharacter], bool]:
    changed = False
    if action.operation == "remove":
        new_list = [c for c in existing if c.char_name != action.char_name]
        changed = len(new_list) != len(existing)
        return new_list, changed

    if action.operation in ("add", "update"):
        # Find by name
        idx = next((i for i, c in enumerate(existing) if c.char_name == action.char_name), None)
        if action.operation == "add":
            if idx is not None:
                # If already exists, treat as update
                target = existing[idx]
                updated = NPCCharacter(
                    char_name=target.char_name,
                    char_age=action.char_age or target.char_age,
                    char_background=action.char_background or target.char_background,
                    char_personality=action.char_personality or target.char_personality,
                    visual_description=action.visual_description or target.visual_description,
                )
                if updated != target:
                    existing[idx] = updated
                    changed = True
                return existing, changed
            # Create new
            new = NPCCharacter(
                char_name=action.char_name,
                char_age=action.char_age or "",
                char_background=action.char_background or "",
                char_personality=action.char_personality or "",
                visual_description=action.visual_description or "",
            )
            existing.append(new)
            return existing, True

        # update
        if idx is None:
            # If not found, ignore update
            return existing, False
        target = existing[idx]
        updated = NPCCharacter(
            char_name=target.char_name,
            char_age=action.char_age or target.char_age,
            char_background=action.char_background or target.char_background,
            char_personality=action.char_personality or target.char_personality,
            visual_description=action.visual_description or target.visual_description,
        )
        if updated != target:
            existing[idx] = updated
            changed = True
        return existing, changed

    return existing, False


def apply_npc_updates(existing: List[NPCCharacter], updates: NPCUpdates) -> Tuple[List[NPCCharacter], bool]:
    """Apply updates, returning (updated_list, changed_flag)."""
    changed_any = False
    current = list(existing)
    for action in updates.actions:
        current, changed = _apply_action(current, action)
        logger.info(
            "NPC action %s for '%s'. Fields: age='%s', background='%s', personality='%s', visual_description='%s'. %s",
            action.operation,
            action.char_name,
            action.char_age,
            action.char_background,
            action.char_personality,
            action.visual_description,
            "applied" if changed else "no-op",
        )
        changed_any = changed_any or changed
    return current, changed_any


async def maybe_update_npcs(state: UserState, scene_description: str, last_choice: str = "") -> bool:
    """Run NPC update agent if enabled. Returns True if state was changed."""
    if not state.story_frame:
        return False

    updates = await propose_npc_updates(state, scene_description, last_choice)
    updated_list, changed = apply_npc_updates(state.story_frame.npc_characters, updates)
    if changed:
        state.story_frame.npc_characters = updated_list
        logger.info("NPC list updated; total NPCs: %d", len(updated_list))
    else:
        logger.info("NPC list unchanged")
    return changed


