from pydantic import BaseModel, Field
from typing import Optional
from src.game.agent.llm import create_light_llm
from langchain_core.messages import SystemMessage, HumanMessage
from src.game.agent.prompts import GAME_STATE_PROMPT
import logging
from src.game.agent.utils import with_retries
from src.game.agent.models import UserState

logger = logging.getLogger(__name__)


IMAGE_GENERATION_SYSTEM_PROMPT = """You are an AI agent for a visual novel game.
Your role is to process an incoming scene description and determine if the visual scene needs to change.
If it does, you will generate a new `scene_description`. This `scene_description` MUST BE a highly detailed image prompt, specifically engineered for an AI image generation model.

**Guidelines for Crafting the Image Prompt (for `scene_description` field):**
When generating the image prompt, ensure it's detailed and considers the following aspects:

1.  **Subject & Focus:**
    *   What is the primary subject or point of interest directly in the character's view?
    *   Describe any other characters visible to the POV character: their appearance (from the character's perspective), clothing, expressions, posture, and actions.
    *   NEVER describe the protagonist/player character in the image prompt.
    *   Detail key objects, items, or environmental elements the character is interacting with or observing.

2.  **Setting & Environment:**
    *   Describe the immediate surroundings as the character would see them.
    *   Time of day and weather conditions as perceived by the character.
    *   Specific architectural or natural features visible in the character's field of view.

3.  **Art Style & Medium:**
    *   Specify the desired visual style (e.g., photorealistic, anime, manga, watercolor, oil painting, pixel art, 3D render, concept art, comic book).
    *   Mention any specific artist influences if relevant (e.g., "in the style of Studio Ghibli").

4.  **Composition & Framing:**
    *   How is the scene framed from the character's eyes? (e.g., "looking straight ahead at a door," "view through a sniper scope," "gazing up at a tall tower").
    *   Describe the arrangement of elements as perceived by the character. Avoid terms like "medium shot" or "wide shot" unless they can be rephrased (e.g., "a wide vista opens up before the viewer").

5.  **Lighting & Atmosphere:**
    *   Describe lighting conditions (e.g., "bright sunlight streams through the window in front of me," "only the dim glow of my flashlight illuminates the passage ahead," "neon signs reflect off the wet street I'm looking at").
    *   What is the overall mood or atmosphere from the character's perspective? (e.g., "a tense silence hangs in the air as I look down the dark hallway," "a sense of peace as I gaze at the sunset over the mountains").

6.  **Color Palette:**
    *   Specify dominant colors or a color scheme relevant to what the character sees.

7.  **Camera & Lens Details (optional but recommended):**
    *   To influence the field of view and photographic feel, you may specify a lens type and focal length—e.g., "macro 60 mm" for detailed close-ups, "telephoto zoom 250 mm" for distant action, or "wide-angle 14 mm" for sweeping vistas. These values follow the guidance in Google’s Gemini image-generation documentation [link](https://ai.google.dev/gemini-api/docs/image-generation).
    *   Mention camera style or sensor type if it helps (e.g., "35 mm film, Portra 400" or "full-frame DSLR").

8.  **Details & Keywords:**
    *   Include crucial details from the input scene description that the character would notice.
    *   Use evocative adjectives and strong, domain-specific keywords.

**Example for the `scene_description` field (the image prompt):**
"Through the cockpit window of a futuristic hovercar, a sprawling neon-lit cyberpunk city stretches out under a stormy, rain-lashed sky. Rain streaks across the glass. The hum of the engine is palpable. Photorealistic, Blade Runner style. Cool blue and vibrant pink neon palette."
"""


class ChangeScene(BaseModel):
    change_scene: bool = Field(
        description="Whether the scene should be changed"
    )
    scene_description: Optional[str] = None

async def generate_image_prompt(state: UserState, scene_description: str, last_choice = "No choice yet") -> ChangeScene:
    """
    Generates a detailed image prompt string based on a scene description.
    This prompt is intended for use with an AI image generation model.
    """
    scene = GAME_STATE_PROMPT.format(
        lore=state.story_frame.lore,
        goal=state.story_frame.goal,
        milestones=",".join(m.id for m in state.story_frame.milestones),
        endings=",".join(e.id for e in state.story_frame.endings),
        history="; ".join(f"{c.scene_id}:{c.choice_text}" for c in state.user_choices),
        last_choice=last_choice,
        scene_description=scene_description
    )
    
    image_prompt_generator_llm = create_light_llm(0.1).with_structured_output(ChangeScene)

    response = await with_retries(lambda: image_prompt_generator_llm.ainvoke(
        [
            SystemMessage(content=IMAGE_GENERATION_SYSTEM_PROMPT),
            HumanMessage(content=scene),
        ]
    ))
    logger.debug("Image prompt generated")
    return response
