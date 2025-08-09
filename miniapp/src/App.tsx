import { BottomBar } from "@/components/BottomBar/BottomBar";
import { Topbar } from "@/components/Topbar/Topbar";
import { PlanUpgradePage } from "@/pages/plan/PlanUpgradePage";
import { RealmsPage } from "@/pages/realms/RealmsPage";
import { SettingsPage } from "@/pages/settings/SettingsPage";
import { StorePage } from "@/pages/store/StorePage";
import { StoryPage } from "@/pages/story/StoryPage";
import { navigationStore } from "@/stores/NavigationStore";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Loader2 } from "lucide-react";
import { observer } from "mobx-react-lite";
import { Suspense, useEffect, useMemo, useState } from "react";
import { usePrefetchData } from "./hooks/usePrefetchData";
import { useSyncLanguageToApp } from "./hooks/useSetInitialLanguage";
import type { CurrentScreen } from "@/components/Topbar/topbar.model";

const screens = {
  realms: RealmsPage,
  story: StoryPage,
  settings: SettingsPage,
  plan: PlanUpgradePage,
  store: StorePage,
};

const queryClient = new QueryClient();

function AppWithProviders() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppBase />
    </QueryClientProvider>
  );
}

const AppBase = observer(() => {
  const screen = navigationStore.currentScreen;

  usePrefetchData();
  useSyncLanguageToApp();

  // Keep previously visited screens mounted to prevent image re-mount flashes
  const [mountedScreens, setMountedScreens] = useState<CurrentScreen[]>([screen]);

  useEffect(() => {
    setMountedScreens((prev) => (prev.includes(screen) ? prev : [...prev, screen]));
  }, [screen]);

  const fallback = useMemo(
    () => (
      <div className="flex items-center justify-center min-h-[80vh]">
        <Loader2 className="w-16 h-16 animate-spin" />
      </div>
    ),
    []
  );

  return (
    <>
      <Topbar selectedScreen={screen} />

      <div className="relative">
        {mountedScreens.map((key) => {
          const ScreenComponent = screens[key];
          const isActive = key === screen;
          return (
            <div key={key} style={{ display: isActive ? "block" : "none" }}>
              <Suspense fallback={fallback}>
                <ScreenComponent />
              </Suspense>
            </div>
          );
        })}
      </div>

      {screen !== "story" && <BottomBar />}
    </>
  );
});

export default AppWithProviders;
