import { observer } from "mobx-react-lite";
import { Suspense } from "react";
import { Loader2 } from "lucide-react";
import { Topbar } from "@/components/Topbar/Topbar";
import { RealmsPage } from "@/pages/realms/RealmsPage";
import { StoryPage } from "@/pages/story/StoryPage";
import { BottomBar } from "@/components/BottomBar/BottomBar";
import { SettingsPage } from "@/pages/settings/SettingsPage";
import { PlanUpgradePage } from "@/pages/plan/PlanUpgradePage";
import { StorePage } from "@/pages/store/StorePage";
import { navigationStore } from "@/stores/NavigationStore";
import { QueryClient, QueryClientProvider, usePrefetchQuery } from "@tanstack/react-query";
import { getPlans, getSubscriptionPlan } from "./api/plans";

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

  usePrefetchQuery({
    queryKey: ["plans"],
    queryFn: getPlans,
  });

  usePrefetchQuery({
    queryKey: ["subscription"],
    queryFn: getSubscriptionPlan,
  });

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
