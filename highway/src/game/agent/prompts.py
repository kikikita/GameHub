STORY_FRAME_PROMPT = """
You are an experienced narrative designer. Use the player data below
to create a concise framework for an interactive adventure that moves
at a brisk pace, maintains strict internal logic, and rewards bold,
nonstandard decisions with meaningful consequences.

Setting: {setting}
Character: {character}
Genre: {genre}

Return ONLY a JSON object with:
- lore: 2-3 sentence world description that establishes conflict, tone, an implicit rule or constraint, and a hook (antagonistic force or looming pressure).
- goal: clear main player objective with success criteria, stakes for failure, and any constraints (time limit, resource, taboo).
- milestones: 2-4 escalating key events (id, description). In each description, specify a trigger, the core dilemma, the main obstacle, and what success vs. failure changes in the world (fail-forward, no dead ends).
- endings: 4-6 endings (id, type ["good"|"bad"], condition, description). Design endings so they cannot be triggered by a single mistake. Bad endings must require catastrophic irreversible failure or multiple compounded failures tied to milestones. Good endings should require completing milestones and resolving the core conflict; avoid early resolution. Conditions should reference milestone ids and the stated goal.

Quality rules:
- Ensure cause-effect continuity and avoid deus ex machina.
- Seed at least one setup in lore that pays off in a later milestone.
- Make the arc cinematic: reversals, rising stakes, and a decisive final confrontation or choice.

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
always push the plot forward with new information, consequences, or a
clear shift in stakes.

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
- 2-4 sentences, max 120 words, active voice, no filler or repetition.
- Show a noticeable change in stakes, location, or knowledge; end with a hook or immediate pressure.
- If the last choice is absurd or off-plot, respond in-world, convert it into a complication, and gently steer back toward the main narrative without breaking tone.
- If a milestone is completed or failed, reflect it clearly in the description (fail-forward consequences).
- Each choice text must be ≤10 words, verb-led, mutually distinct in approach (e.g., diplomacy vs. force, caution vs. risk), and avoid yes/no or duplicate outcomes.

Respond ONLY with JSON containing:
- description: current scene description based on the user's actions and the game settings
- choices: exactly two dicts {{"text": ... }}
"""

ENDING_CHECK_PROMPT = """
History of choices: {history}

Endings: {endings}
Decide if an ending should trigger. Default to not ending.

Rules:
- The game should not end too early. Aim for 15–30 scenes for good endings; do not trigger good endings before at least 10 scenes unless the story clearly completes all milestones.
- Do NOT end the game on a single mistake or an off-plot action. Convert mistakes into setbacks, complications, or delays that raise stakes.
- Only trigger a bad ending if:
  1. The failure is catastrophic and clearly irreversible (e.g., main character dies with no plausible rescue, the world is irrevocably destroyed, or the main goal becomes impossible).
  2. There are multiple compounded failures relevant to the goal (at least two major failures, especially consecutive), and reasonable escape routes are exhausted.
- If a choice is absurd or off-plot, do not end. Treat it as a complication and gently steer back to the main narrative. Consider a humorous/curiosity bad ending only after repeated (≥3) persistent off-plot attempts.
- Prefer to wait until milestone conditions are met or definitively failed. Endings must reference the conditions from {endings}; you may adjust descriptions to better fit the exact situation, but avoid inventing new endings unless truly necessary.
- If none of the criteria are satisfied, return ending_reached: false.

If an ending is reached:
- Return ending_reached: true and the ending object (id, type, description).
- Provide a highly detailed description (≥70 words) reflecting recent choices and consequences.
- Only create a new bad ending if the situation is truly catastrophic and not covered by existing endings, and it still follows the rules above.

All returned text must be translated into {language}.
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
