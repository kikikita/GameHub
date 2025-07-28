
export interface RealmDTO {
    id: string;
    title: string;
    description: string;
    imageUrl: string;
}

export interface RealmResponse {
    realms: RealmDTO[];
}

export async function getRealms(): Promise<RealmResponse> {
    // Return mock data matching the image
    return {
        realms: [
            {
                id: "noir-city",
                title: "Noir City",
                description: "Gritty detective",
                imageUrl: "https://cdnb.artstation.com/p/assets/images/images/006/361/597/large/eddie-mendoza-project-noir.jpg?1498006617", // No image shown in the screenshot
            },
            {
                id: "solar-eden",
                title: "Solar Eden",
                description: "Futuristic utopia",
                imageUrl: "https://thumbs.dreamstime.com/b/new-eden-futuristic-underwater-city-population-desig-new-eden-futuristic-underwater-city-population-370835114.jpg",
            },
            {
                id: "college-life",
                title: "College Life",
                description: "Realistic",
                imageUrl: "https://campus-life.brown.edu/sites/default/files/styles/ultrawide_med/public/2024-01/20191020_COMM_coheamarketing117-3.jpg?h=064723c3&itok=P7tmLheA",
            },
            {
                id: "mystery-forest",
                title: "Mystery Forest",
                description: "Surreal & eerie",
                imageUrl: "https://thumbs.dreamstime.com/b/mysterious-retro-tv-glow-foggy-forest-surreal-design-concept-art-static-filled-emits-soft-dense-fog-laden-eerie-368106283.jpg",
            },
        ],
    };
}
