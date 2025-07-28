import { navigationStore } from "@/stores/NavigationStore";
import type { CurrentScreen } from "@/components/Topbar/topbar.model";
import { Joystick, Settings } from "lucide-react";
import clsx from "clsx";

const items: Array<{
  id: CurrentScreen;
  label: string;
  icon: React.ReactElement;
}> = [
  {
    id: "realms",
    label: "Realms",
    icon: <Joystick />,
  },
  {
    id: "settings",
    label: "Settings",
    icon: <Settings />,
  },
];

export function BottomBar() {
  const current = navigationStore.currentScreen;

  const handleNavigate = (screen: CurrentScreen) => {
    navigationStore.setScreen(screen);
  };

  return (
    <>
      <div className="h-18" />
      <nav className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 flex bg-background/80 backdrop-blur-md border border-border shadow-md rounded-full">
        {items.map(({ id, icon, label }) => (
          <button
            key={id}
            aria-label={label}
            onClick={() => handleNavigate(id)}
            className={clsx(
              "flex flex-col items-center text-xs transition-colors px-5 py-3 cursor-pointer",
              current === id ? "text-foreground" : "text-muted-foreground"
            )}
          >
            {icon}
          </button>
        ))}
      </nav>
    </>
  );
}
