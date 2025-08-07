STORY_FRAME_PROMPT = """
You are an experienced narrative designer. Use the player profile below
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

All returned text must be in {language}.
"""

GAME_STATE_PROMPT = """
---Game Settings START---
Lore: {lore}
Goal: {goal}
Milestones: {milestones}
Endings: {endings}
World visual style: {visual_style}
NPC characters: {npc_characters}
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
- Each choice text must be ≤12 words and lead to distinct outcomes.

Respond ONLY with JSON containing:
- description: scene description
- choices: exactly two dicts {{"text": ..., "next_scene_short_desc": ...}}
"""

ENDING_CHECK_PROMPT = """
History: {history}
Endings: {endings}
Check if any ending conditions are met.
If none are met return ending_reached: false.
If an ending is reached return ending_reached: true and provide the
ending object (id, type, description).
Respond ONLY with JSON.
"""
