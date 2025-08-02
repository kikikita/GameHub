STORY_FRAME_PROMPT = """
You are a narrative game designer. Use the player data below to
create a story frame for an interactive adventure.
Setting: {setting}
Character: {character}
Genre: {genre}
Return ONLY a JSON object with:
- lore: brief world description
- goal: main player objective
- milestones: 2-4 key events (id, description)
- endings: good/bad endings (id, type, condition, description)

Translate the lore, goal, milestones and endings to the language which is used in the game and setting description.
"""

GAME_STATE_PROMPT = """
---Game Settings START---
Lore: {lore}
Goal: {goal}
Milestones: {milestones}
Endings: {endings}
---Game Settings END---

---User's actions START---
History: {history}
Last choice: {last_choice}
Last image description: {image_description}
---User's actions END---

Game response to user's action: {scene_description}
"""

SCENE_PROMPT = """You are an AI agent for a visual novel game. 
Your role is to process incoming data and generate the next scene description and choices.
Translate the scene description and choices into a language which is used in the Game Settings.

---Game Settings START---
Lore: {lore}
Goal: {goal}
Milestones: {milestones}
Endings: {endings}
---Game Settings END---

---User's actions START---
History: {history}
Last choice: {last_choice}
---User's actions END---

The scene description must be 2-5 sentences and no more than 150 words.
Each choice text must be concise, up to 12 words.
Respond ONLY with JSON containing:
- description: current scene description based on the user's actions and the game settings
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
