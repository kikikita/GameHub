import { Plus } from "lucide-react";

export interface WishesIndicatorProps {
  /** Current amount of wishes available to the user */
  wishes: number;
  /** Callback fired when user presses the plus button */
  onAddWishes?: () => void;
}

/**
 * Small pill-shaped indicator that shows current wishes balance.
 * Designed to be placed inside the Topbar on the right side.
 */
export function WishesIndicator({ wishes, onAddWishes }: WishesIndicatorProps) {
  return (
    <button
      type="button"
      onClick={onAddWishes}
      className="flex items-center gap-1 rounded-full bg-primary/20 px-3 py-0.5 text-sm font-medium text-foreground/90 backdrop-blur-sm hover:bg-primary/30 active:bg-primary/40 transition-colors"
    >
      <span className="text-base leading-none">✨</span>
      <span className="leading-none">{wishes}</span>
      <span className="mx-1 h-3 w-px bg-border/50" />
      <Plus className="h-4 w-4" />
    </button>
  );
} 