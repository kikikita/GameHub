import type { CurrentScreen } from "@/components/Topbar/topbar.model";
import { makeAutoObservable } from "mobx";

export class NavigationStore {
    constructor() {
        makeAutoObservable(this);
    }

    /**
     * Keeps track of the visited screens in the order the user navigated.
     * The very first screen is always "realms".
     */
    private history: CurrentScreen[] = ["realms"];

    /**
     * Current screen derives from the last item in the history stack.
     * We keep it as an observable field so existing components relying on it continue working.
     */
    currentScreen: CurrentScreen = "realms";

    /** ID of selected realm when in story view */
    selectedRealmId: string | null = null;

    /**
     * Navigate to the provided screen.
     * - If navigating to the initial "realms" screen, it resets history.
     * - Otherwise, it pushes the screen onto the history stack (if it is not already the current one).
     */
    setScreen(screen: CurrentScreen) {
        if (screen === "realms") {
            // Reset navigation history when returning to the main screen.
            this.history = ["realms"];
        } else if (this.currentScreen !== screen) {
            this.history.push(screen);
        }

        this.currentScreen = screen;
    }

    /** Select a realm and navigate to story screen */
    selectRealm(id: string) {
        this.selectedRealmId = id;
        this.setScreen("story");
    }

    /**
     * Returns true if there is somewhere to go back to (i.e., history depth > 1).
     */
    get canGoBack() {
        return this.history.length > 1;
    }

    /**
     * Go to the previous screen if possible.
     * Does nothing when already on the initial screen.
     */
    goBack() {
        if (this.history.length > 1) {
            // Remove current screen
            this.history.pop();
            // Set new current screen
            this.currentScreen = this.history[this.history.length - 1];
        }
    }
}

export const navigationStore = new NavigationStore();