export interface StoryDTO {
  id: string;
  title: string;
  description: string;
  imageUrl: string;
}

export interface StoryResponse {
  stories: StoryDTO[];
}

// Temporary mock implementation until backend is ready
export async function getStories(_realmId: string): Promise<StoryResponse> {
  // For demo, ignoring realmId and returning generic content
  return {
    stories: [
      {
        id: "hot-neighbor",
        title: "Hot Neighbor",
        description: "Your floor's hot neighbor has nowhere to sleep!",
        imageUrl:
          "https://www.abilitybathedevon.co.uk/wp-content/uploads/2023/11/image-1-1.png",
      },
      {
        id: "stepmom-shower",
        title: "Stepmom Shower",
        description: "Your stepmom forgot to lock the bathroom door...",
        imageUrl:
          "https://www.abilitybathedevon.co.uk/wp-content/uploads/2023/11/image-1-1.png",
      },
    ],
  };
} 