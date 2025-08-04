import { cn } from "@/utils/cn";
import newStoryBackground from "@/assets/images/new_story_background.webp";
import { useUser } from "@/api/user";
import { navigationStore } from "@/stores/NavigationStore";
import { useTranslation } from "react-i18next";
import { createStory } from "@/api/stories";
import { exitMiniApp } from "@/telegram/exit";
import { useCallback } from "react";

const NEW_STORY_COST = 5;

interface CreateNewStoryCardProps {
  className?: string;
}

export function CreateNewStoryCard({ className }: CreateNewStoryCardProps   ) {
  const { t } = useTranslation();
  const {
    data: { wishes },
  } = useUser();

  const title = t("createNewStoryCard:createStory", { defaultValue: "Create a Story" });
  const words = title.split(" ");
  const firstLine = words.slice(0, words.length - 1).join(" ");
  const secondLine = words[words.length - 1] ?? "";

  const handleClick = useCallback(async () => {
    if (wishes < NEW_STORY_COST) {
      navigationStore.setScreen("store");
      return;
    }
    await createStory();
    exitMiniApp();
  }, [wishes]);

  return (
    <button
      type="button"
      onClick={handleClick}
      className={cn(
        "relative overflow-hidden rounded-xl bg-muted select-none text-left cursor-pointer w-full",
        className,
      )}
    >
      {/* Background */}
      <img
        src={newStoryBackground}
        alt={t("createNewStoryCard:createStory", { defaultValue: "Create a Story" })}
        className="h-full w-full object-cover"
        loading="lazy"
      />

      {/* Title */}
      <div className="absolute inset-x-0 top-0 p-3 pointer-events-none">
        <h3 className="text-xl sm:text-2xl font-bold text-white drop-shadow-sm leading-snug whitespace-pre-line">
          <span className="block">{firstLine}</span>
          {secondLine && <span className="block">{secondLine}</span>}
        </h3>
      </div>

      {/* Cost badge */}
      <div className="absolute inset-x-0 bottom-0 p-3 pointer-events-none flex">
        <span className="inline-flex items-center gap-1 rounded-full bg-black/60 px-2 py-0.5 text-sm font-medium text-white">
          <span className="leading-none">✨</span>
          <span>{NEW_STORY_COST}</span>
        </span>
      </div>
    </button>
  );
}
