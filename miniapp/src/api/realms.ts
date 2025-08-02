import { useSuspenseQuery } from "@tanstack/react-query";
import { API_URL } from "./common";

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

export function getRealms(): Promise<Realm[]> {
  return fetch(`${API_URL}/api/v1/worlds/`).then((res) =>
    res.json()
  ).then<Realm[]>((data) => data.map((item: WorldDTO) => ({
    id: item.id,
    title: item.title,
    description: item.world_desc,
    imageUrl: item.image_url,
  })));
}

export function useRealms() {
  return useSuspenseQuery({
    queryKey: ["worlds"],
    queryFn: getRealms,
  });
}