import { useSuspenseQuery } from "@tanstack/react-query";
import { API_URL } from "./common";
import { useTranslation } from "react-i18next";

export interface Realm {
  id: string;
  title: string;
  description: string;
  imageUrl: string;
}

export interface WorldDTO {
  id: string;
  title: string;
  world_desc: string;
  image_url: string;
}

export function getRealms(lang: string = "en"): Promise<Realm[]> {
  return fetch(`${API_URL}/api/v1/worlds/?lang=${lang}`).then((res) =>
    res.json()
  ).then<Realm[]>((data) => data.map((item: WorldDTO) => ({
    id: item.id,
    title: item.title,
    description: item.world_desc,
    imageUrl: item.image_url,
  })));
}

export function useRealms() {
  const { i18n } = useTranslation();

  return useSuspenseQuery({
    queryKey: ["worlds", i18n.language],
    queryFn: () => getRealms(i18n.language),
  });
}