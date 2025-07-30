
export interface RealmDTO {
    id: string;
    title: string;
    description: string;
    imageUrl: string;
}

export interface RealmResponse {
    realms: RealmDTO[];
}

import { API_URL } from "./common";

export async function getRealms(): Promise<RealmResponse> {
    const resp = await fetch(`${API_URL}/worlds`);
    if (!resp.ok) {
        throw new Error("Failed to fetch worlds");
    }
    const data = await resp.json();
    return {
        realms: data.map((w: any) => ({
            id: w.id,
            title: w.title,
            description: w.setting_desc,
            imageUrl: w.image_url || "",
        })),
    };
}
