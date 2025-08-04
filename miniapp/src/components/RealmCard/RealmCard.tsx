import { cn } from "@/utils/cn";
import fallbackImage from "@/assets/images/new_story_background.webp";

interface RealmCardProps {
  /**
   * The main title of the realm.
   */
  title: string;
  /**
   * A short subtitle or description shown below the title.
   */
  description?: string;
  /**
   * URL of the picture that will be displayed as the card background.
   */
  imageUrl: string;
  /**
   * Additional classes to merge with the default styles.
   */
  className?: string;

  /** Called when the user clicks the card */
  onClick?: () => void;
}

/**
 * RealmCard renders a clickable card with a background image and an overlay
 * containing a title and optional description.
 *
 * The component is deliberately kept presentational – any click handling or
 * routing logic should be implemented by the consuming component via a wrapper
 * element or by passing `onClick` through `className` (e.g. using `asChild`).
 */
export function RealmCard({
  title,
  description,
  imageUrl,
  className,
  onClick,
}: RealmCardProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "relative overflow-hidden rounded-xl bg-muted select-none text-left cursor-pointer",
        className
      )}
    >
      <img
        src={imageUrl ?? fallbackImage}
        onError={(e) => {
          if (e.currentTarget.src !== fallbackImage) {
            e.currentTarget.src = fallbackImage;
          }
        }}
        alt={title}
        className="h-full w-full object-cover"
        loading="lazy"
      />
      <div className="absolute inset-x-0 top-0 p-3 pointer-events-none">
        <h3
          className="text-xl sm:text-2xl font-bold text-white leading-snug"
          style={{ textShadow: "0 0 5px rgba(0, 0, 0, 0.5)" }}
        >
          {title}
        </h3>
      </div>
      {description && (
        <div className="absolute inset-x-0 bottom-0 p-3 pointer-events-none backdrop-blur-[2px]">
          <p className="text-sm text-white/80 drop-shadow-sm">{description}</p>
        </div>
      )}
    </button>
  );
}