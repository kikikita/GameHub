import { closeMiniApp, isTMA } from "@telegram-apps/sdk";

/**
 * Exits the Telegram Mini App if running inside Telegram.
 * If not in Telegram, does nothing.
 */
export function exitMiniApp() {
  if (isTMA()) {
    closeMiniApp();
  }
}
