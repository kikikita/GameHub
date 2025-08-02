import { Plus } from "lucide-react";
import { useSubscriptionPlan } from "@/api/plans";

export interface ResourcesIndicatorProps {
  wishes: number;
  energyCurrent: number;
  energyMax: number;
  /** Fired when user clicks the plus button */
  onAdd?: () => void;
}

export function ResourcesIndicator({
  wishes,
  energyCurrent,
  energyMax,
  onAdd,
}: ResourcesIndicatorProps) {
  const {
    data: { plan },
  } = useSubscriptionPlan();
  const isPro = plan === "pro";
  return (
    <button
      type="button"
      onClick={onAdd}
      className="flex items-center rounded-full bg-muted px-2 py-0.5 text-sm font-medium gap-1 hover:bg-muted/80 active:bg-muted/70 transition-colors border border-border cursor-pointer"
    >
      <span className="flex items-center gap-1">
        <span className="text-base leading-none">✨</span>
        <span>{wishes}</span>
      </span>

      <span className="mx-1 w-px h-5 bg-primary/30" />

      <span className="flex items-center gap-1">
        <span className="text-base leading-none">⚡</span>
        {isPro ? (
          <span className="flex items-center justify-center w-5 h-2 text-lg">∞</span>
        ) : (
          <span>
            {energyCurrent}/{energyMax}
          </span>
        )}
      </span>

      <span className="mx-1 w-px h-5 bg-primary/30" />
      <Plus className="h-4 w-4" />
    </button>
  );
}
