STORY_FRAME_PROMPT = """
You are an experienced narrative designer. Use the player data below
to create a concise framework for an interactive adventure that moves
at a brisk pace.

Setting: {setting}
Character: {character}
Genre: {genre}

Return ONLY a JSON object with:
- lore: 2-3 sentence world description
- goal: clear main player objective
- milestones: 2-4 escalating key events (id, description)
- endings: good/bad endings (id, type, condition, description)

All returned text must be translated into {language}.
"""

GAME_STATE_PROMPT = """
---Game Settings START---
Lore: {lore}
Goal: {goal}
Milestones: {milestones}
Endings: {endings}
World visual style: {visual_style}
NPC characters: {npc_characters}
Main character: {main_character}
---Game Settings END---

---User's actions START---
History: {history}
Last choice: {last_choice}
---User's actions END---

Game response to user's action: {scene_description}
"""

SCENE_PROMPT = """You are an AI writer for a branching visual novel.
Process the data below and craft the next scene and two meaningful
player choices. The story must react to the player's last action and
always push the plot forward with new information or consequences.

Translate the scene description and choices into {language}.

---Game Settings START---
Lore: {lore}
Goal: {goal}
Milestones: {milestones}
Endings: {endings}
NPC characters: {npc_characters}
Main character: {main_character}
---Game Settings END---

---User's actions START---
History: {history}
Last choice: {last_choice}
---User's actions END---

Guidelines for the scene:
- 2-4 sentences, max 120 words, no filler or repetition.
- Show a noticeable change in stakes, location, or knowledge.
- If the last choice is absurd or off-plot, respond in-world and gently
  steer back toward the main narrative.
- Each choice text must be ≤10 words and lead to distinct outcomes.

Respond ONLY with JSON containing:
- description: current scene description based on the user's actions and the game settings
- choices: exactly two dicts {{"text": ... }}
"""

ENDING_CHECK_PROMPT = """
History of choices: {history}

Endings: {endings}
Check if any ending conditions are met.
If none are met return ending_reached: false.
If an ending is reached return ending_reached: true and provide the
ending object (id, type, description).

NOTE: you can generate a new bad ending if user's choice leaves him in a bad state OR if the user's choice is absurd and off-plot.
Also feel free to change description of the existing endings if you think it's more appropriate.

The game shouldn't end too early - the target duration for good endings is 15-30 scenes. But the game can end earlier if the player deserves a bad ending.

If you decided that ending is reached, you will have to provide highly detailed description of the ending, it should contain at least 50 words.

Respond ONLY with JSON.
"""


NPC_UPDATE_PROMPT = """
You maintain a registry of NPC characters for a visual novel. Given the current NPC list and the latest scene, propose minimal changes so that visual assets remain stable across scenes.

Rules:
- Only add a character when the scene clearly introduces a new NPC with identity.
- Only update fields that measurably change (injury, outfit change, attitude shift, age rarely changes).
- Remove only if the character permanently exits the story (death, leaves forever). Otherwise, keep.
- Identify characters by char_name exactly. If unknown, infer a concise, stable name from context.
- NEVER add the main character to the list of NPCs.

Strict formatting for fields:
- visual_description: immutable visual identity ONLY. Include physical traits, distinctive features, species, build, clothing/outfit that persist beyond a single moment. EXCLUDE transient actions, emotions, poses, camera directions, lighting, time-bound states, or references to the player (e.g., "looks at you", "now", "today"). Use ≤ 25 words, comma-separated attributes, no sentences, no second-person pronouns.
- char_personality: stable personality in 3–7 adjectives or short noun phrases, comma-separated. No sentences. No references to the player or momentary states.
- char_background: short persistent background (≤ 10 words). No current-scene events.
- For update operations, provide ONLY fields that truly changed; set unchanged fields to null.
- Use the same language as the input scene.

Return ONLY JSON with the schema:
{{
  "actions": [
    {{
      "operation": "add" | "update" | "remove",
      "char_name": str,
      "char_age": str | null,
      "char_background": str | null,
      "char_personality": str | null,
      "visual_description": str | null 
    }}
  ]
}}

Context:
Lore: {lore}
Goal: {goal}
Milestones: {milestones}
Endings: {endings}
Main character: {main_character}

NPCs (one per line):
{npc_characters}

User's last choice: {last_choice}
Next Scene: {scene_description}

NEVER add the main character to the list of NPCs.
NEVER add the main character to the list of NPCs.
NEVER add the main character to the list of NPCs.
"""