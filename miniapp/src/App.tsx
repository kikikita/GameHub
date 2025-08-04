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
import { Suspense } from "react";
import { usePrefetchData } from "./hooks/usePrefetchData";
import { useSyncLanguageToApp } from "./hooks/useSetInitialLanguage";

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

  const Screen = screens[screen];

  usePrefetchData();
  useSyncLanguageToApp();

  return (
    <>
      <Topbar selectedScreen={screen} />
      <Suspense
        fallback={
          <div className="flex items-center justify-center min-h-[80vh]">
            <Loader2 className="w-16 h-16 animate-spin" />
          </div>
        }
      >
        <Screen />
      </Suspense>
      {screen !== "story" && <BottomBar />}
    </>
  );
});

export default AppWithProviders;
