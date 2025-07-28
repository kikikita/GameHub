import { backButton, isTMA } from "@telegram-apps/sdk";
import { autorun } from "mobx";
import { navigationStore } from "@/stores/NavigationStore";

/**
 * Initializes Telegram BackButton behaviour:
 * 1. Shows the button only when we are **not** on the initial "realms" screen.
 * 2. Handles button clicks and returns the user to the previous screen (realms).
 *
 * This helper must be executed once on application startup **after** the SDK init.
 */
export function initBackButton() {
  if (!isTMA()) return;

  // Mount component if supported.
  try {
    if (backButton.mount?.isAvailable?.()) {
      backButton.mount();
    }
  } catch {
    /* noop – not critical */
  }

  // Register a click handler that navigates back to the realms screen.
  try {
    // Some SDK versions expose onClick() directly.
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const btn: any = backButton;
    if (btn.onClick?.isAvailable?.()) {
      btn.onClick(() => navigationStore.goBack());
    } else if (typeof btn.onClick === "function") {
      btn.onClick(() => navigationStore.goBack());
    }
  } catch {
    /* noop – not critical */
  }

  // Reactively show / hide button depending on current screen.
  autorun(() => {
    const shouldShow = navigationStore.canGoBack;

    if (shouldShow) {
      backButton.show?.ifAvailable?.();
    } else {
      backButton.hide?.ifAvailable?.();
    }
  });
} 