import { getStories } from "@/api/stories";
import { StoryCard } from "@/components/StoryCard/StoryCard";
import { use } from "react";
import { exitMiniApp } from "@/telegram/exit";
import { navigationStore } from "@/stores/NavigationStore";

const storiesPromise = getStories(navigationStore.selectedRealmId || '')

export function StoryPage() {
  const stories = use(storiesPromise);

  const handleExit = () => {
    exitMiniApp();
  }

  return (
    <div className="p-2 space-y-4">
      {stories.stories.map((story) => (
        <StoryCard key={story.id} {...story} className="aspect-video" onClick={handleExit} />
      ))}
    </div>
  );
} 