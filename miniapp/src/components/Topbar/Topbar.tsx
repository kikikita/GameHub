import type { CurrentScreen } from "./topbar.model";
import { useTranslation } from "react-i18next";
import { ResourcesIndicator } from "./ResourcesIndicator";
import { navigationStore } from "@/stores/NavigationStore";

export interface TopbarProps {
  selectedScreen: CurrentScreen;
}

export function Topbar({ selectedScreen }: TopbarProps) {
  const { t } = useTranslation('topbar');

  const handleAddResources = () => {
    // Navigate user to the store screen where they can spend or purchase wishes
    navigationStore.setScreen("store");
  };

  return (
    <>
      <nav className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-md border-b border-border h-12 flex items-end justify-between px-4 pt-0 pb-4">
        <span className="text-foreground text-2xl font-medium">
          {t(selectedScreen)}
        </span>
        <ResourcesIndicator onAdd={handleAddResources} />
      </nav>
      <div className="h-12" />
    </>
  );
}