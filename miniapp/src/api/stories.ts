import { useSuspenseQuery } from "@tanstack/react-query";
import { API_URL } from "./common";
import { getInitData } from "@/telegram/init";
import { useTranslation } from "react-i18next";

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
  const { i18n } = useTranslation();
  
  return useSuspenseQuery({
    queryKey: ["stories", realmId, i18n.language],
    queryFn: () => getStories(realmId, i18n.language),
    staleTime: 1000 * 60 * 60 * 24,
  });
}

export async function getStories(realmId: string, lang: string = "en"): Promise<Story[]> {
  return fetch(`${API_URL}/api/v1/worlds/${realmId}/stories/?lang=${lang}`, {
    headers: {
      'Authorization': `tma ${getInitData()}`,
    },
  }).then((res) => res.json()).then((data) => data.map((item: StoryDTO) => ({
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

export async function createStory() {
  return fetch(`${API_URL}/bot/api/v1/stories/`, {
    method: "POST",
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `tma ${getInitData()}`,
    },
  });
}