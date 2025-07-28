import { cn } from "@/utils/cn";

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
      {/* Background image */}
      <img
        src={imageUrl}
        alt={title}
        className="h-full w-full object-cover"
        loading="lazy"
      />

      {/* Text overlay */}
      <div className="absolute inset-x-0 bottom-0 p-3 backdrop-blur-[2px]">
        <h3 className="text-base font-semibold text-white drop-shadow-sm">
          {title}
        </h3>
        {description && (
          <p className="text-sm text-white/80 drop-shadow-sm">{description}</p>
        )}
      </div>
    </button>
  );
}