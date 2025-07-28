import { GoogleGenAI } from "@google/genai";
import { type GeminiToken } from "./model";

export function createGenAI(token: GeminiToken): GoogleGenAI {
  const ai = new GoogleGenAI({
    apiKey: token.name,
    httpOptions: { apiVersion: 'v1alpha' }
  });
  return ai;
}
