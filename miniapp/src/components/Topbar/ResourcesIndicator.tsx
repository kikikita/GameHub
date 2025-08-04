import { Plus } from "lucide-react";
import { useSubscriptionPlan } from "@/api/plans";
import { useUser } from "@/api/user";

export interface ResourcesIndicatorProps {
  /** Fired when user clicks the plus button */
  onAdd?: () => void;
}

const MAX_ENERGY = 50;

export function ResourcesIndicator({
  onAdd,
}: ResourcesIndicatorProps) {
  const {
    data: { plan },
  } = useSubscriptionPlan();
  const {
    data: { wishes, energy },
  } = useUser();
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
            {energy}/{MAX_ENERGY}
          </span>
        )}
      </span>
      <Plus className="h-4 w-4" />
    </button>
  );
}
