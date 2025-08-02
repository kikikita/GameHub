import { startStory, useStories } from "@/api/stories";
import { StoryCard } from "@/components/StoryCard/StoryCard";
import { exitMiniApp } from "@/telegram/exit";
import { navigationStore } from "@/stores/NavigationStore";
import { observer } from "mobx-react-lite";
import { useCallback } from "react";

function StoryPageComponent() {
  const { data: stories } = useStories(navigationStore.selectedRealmId ?? '');

  const handleSelectStory = useCallback(async (storyId: string) => {
    await startStory(storyId);
    exitMiniApp();
  }, []);

  return (
    <div className="p-2 space-y-4">
      {stories.map((story) => (
        <StoryCard key={story.id} {...story} className="aspect-video" onClick={handleSelectStory} />
      ))}
    </div>
  );
} 

export const StoryPage = observer(StoryPageComponent);