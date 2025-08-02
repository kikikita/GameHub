import { useSuspenseQuery } from "@tanstack/react-query";
import { API_URL } from "./common";
import { getInitData } from "@/telegram/init";

export interface StoryDTO {
  id: string;
  title: string;
  story_desc: string;
  genre: string;
  image_url?: string;
}

export interface Story {
  id: string;
  title: string;
  description: string;
  imageUrl: string;
}

export function useStories(realmId: string) {
  return useSuspenseQuery({
    queryKey: ["stories", realmId],
    queryFn: () => getStories(realmId),
  });
}

export async function getStories(realmId: string): Promise<Story[]> {
  return fetch(`${API_URL}/api/v1/worlds/${realmId}/stories/`).then((res) => res.json()).then((data) => data.map((item: StoryDTO) => ({
    id: item.id,
    title: item.title,
    description: item.story_desc,
    imageUrl: item.image_url,
  })));
} 

export async function startStory(storyId: string) {
  return fetch(`${API_URL}/bot/api/v1/stories/start/${storyId}/`, {
    method: "POST",
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `tma ${getInitData()}`,
    },
  });
}