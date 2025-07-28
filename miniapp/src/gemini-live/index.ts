import { createGenAI } from "./genai";
import { LiveMusicHelper } from "./LiveMusicHelper";
import type { Prompt } from "./model";

export function startMusicGeneration() {
  function buildInitialPrompts() {
    // Pick 3 random prompts to start at weight = 1
    const startOn = [...DEFAULT_PROMPTS]
      .sort(() => Math.random() - 0.5)
      .slice(0, 3);

    const prompts = new Map<string, Prompt>();

    for (let i = 0; i < DEFAULT_PROMPTS.length; i++) {
      const promptId = `prompt-${i}`;
      const prompt = DEFAULT_PROMPTS[i];
      const { text, color } = prompt;
      prompts.set(promptId, {
        promptId,
        text,
        weight: startOn.includes(prompt) ? 1 : 0,
        cc: i,
        color,
      });
    }

    return prompts;
  }

  const DEFAULT_PROMPTS = [
    { color: "#9900ff", text: "Bossa Nova" },
    { color: "#5200ff", text: "Chillwave" },
    { color: "#ff25f6", text: "Drum and Bass" },
    { color: "#2af6de", text: "Post Punk" },
    { color: "#ffdd28", text: "Shoegaze" },
    { color: "#2af6de", text: "Funk" },
    { color: "#9900ff", text: "Chiptune" },
    { color: "#3dffab", text: "Lush Strings" },
    { color: "#d8ff3e", text: "Sparkling Arpeggios" },
    { color: "#d9b2ff", text: "Staccato Rhythms" },
    { color: "#3dffab", text: "Punchy Kick" },
    { color: "#ffdd28", text: "Dubstep" },
    { color: "#ff25f6", text: "K Pop" },
    { color: "#d8ff3e", text: "Neo Soul" },
    { color: "#5200ff", text: "Trip Hop" },
    { color: "#d9b2ff", text: "Thrash" },
  ];

  const genAI = createGenAI({
    name: "",
  });

  const liveMusicHelper = new LiveMusicHelper(genAI, "lyria-realtime-exp");
  liveMusicHelper.setWeightedPrompts(buildInitialPrompts());

  liveMusicHelper.playPause();
}
