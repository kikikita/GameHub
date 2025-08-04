import { isTMA } from "@telegram-apps/sdk";

/**
 * Initializes color-scheme synchronization with Telegram.
 *
 * • Adds the `dark` class to <html> whenever the Mini App is opened in dark mode.
 * • Removes the class when Telegram switches back to light mode.
 * • Subscribes to the `themeChanged` event so the UI reacts instantly without reload.
 */
export function initTheme() {
  if (!isTMA()) return;

  const applyScheme = () => {
    // Some clients may not expose colorScheme – default to "light"
    const scheme = window.Telegram?.WebApp?.colorScheme ?? "light";

    if (scheme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  };

  applyScheme();

  try {
    window.Telegram?.WebApp?.onEvent?.("themeChanged", applyScheme);
  } catch {
    /* noop – not critical if the API is unavailable */
  }
}
