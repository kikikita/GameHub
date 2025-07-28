export interface GeminiToken {
  name: string;
}

export interface Prompt {
  readonly promptId: string;
  text: string;
  weight: number;
  cc: number;
  color: string;
}

export interface ControlChange {
  channel: number;
  cc: number;
  value: number;
}

export type PlaybackState = "stopped" | "playing" | "loading" | "paused";
