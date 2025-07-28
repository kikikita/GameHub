export interface StoryDTO {
  id: string;
  title: string;
  description: string;
  imageUrl: string;
}

export interface StoryResponse {
  stories: StoryDTO[];
}

import { API_URL } from "./common";

export async function getStories(): Promise<StoryResponse> {
  const resp = await fetch(`${API_URL}/templates/preset`);
  if (!resp.ok) {
    throw new Error("Failed to fetch stories");
  }
  const data = await resp.json();
  return {
    stories: data.map((t: any) => ({
      id: t.id,
      title: t.title,
      description: t.setting_desc,
      imageUrl: "",
    })),
  };
}