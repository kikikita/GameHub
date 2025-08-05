import { cn } from "@/utils/cn";
import fallbackImage from "@/assets/images/new_story_background.webp";
import { Play } from "lucide-react";

interface StoryCardProps {
  id: string;
  title: string;
  description?: string;
  imageUrl?: string;
  onClick?: (storyId: string) => void;
  className?: string;
}

export function StoryCard({
  id,
  title,
  description,
  imageUrl,
  onClick,
  className,
}: StoryCardProps) {
  return (
    <button
      type="button"
      onClick={() => onClick?.(id)}
      className={cn(
        "w-full relative overflow-hidden rounded-xl bg-muted select-none text-left cursor-pointer",
        className
      )}
    >
      <img
        src={imageUrl || fallbackImage}
        onError={(e) => {
          if (e.currentTarget.src !== fallbackImage) {
            e.currentTarget.src = fallbackImage;
          }
        }}
        alt={title}
        className="h-full w-full object-cover"
        loading="lazy"
      />

      <div className="absolute z-1 inset-0 flex items-center justify-center pointer-events-none">
        <span className="flex h-14 w-14 items-center justify-center rounded-full bg-black/50 backdrop-blur-[2px]">
          <Play className="size-8 text-white" />
        </span>
      </div>

      <div className="absolute inset-x-0 bottom-0 p-3 pointer-events-none backdrop-blur-[2px]">
        <h3 className="text-base font-semibold text-white drop-shadow-sm">
          {title}
        </h3>
        {description && (
          <p className="text-sm text-white/80 drop-shadow-sm">
            {description}
          </p>
        )}
      </div>
    </button>
  );
} 