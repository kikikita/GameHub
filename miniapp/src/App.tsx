import { observer } from "mobx-react-lite";
import { Topbar } from "@/components/Topbar/Topbar";
import { RealmsPage } from "@/pages/realms/RealmsPage";
import { StoryPage } from "@/pages/story/StoryPage";
import { BottomBar } from "@/components/BottomBar/BottomBar";
import { SettingsPage } from "@/pages/settings/SettingsPage";
import { PlanUpgradePage } from "@/pages/plan/PlanUpgradePage";
import { StorePage } from "@/pages/store/StorePage";
import { navigationStore } from "@/stores/NavigationStore";

const screens = {
  realms: RealmsPage,
  story: StoryPage,
  settings: SettingsPage,
  plan: PlanUpgradePage,
  store: StorePage,
}


function AppBase() {
  const screen = navigationStore.currentScreen;

  const Screen = screens[screen];

  return (
    <>
      <Topbar selectedScreen={screen} />
      <Screen />
      {screen !== "story" && <BottomBar />}
    </>
  );
}

const App = observer(AppBase);

export default App;
