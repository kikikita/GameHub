import { viewport, init, isTMA } from "@telegram-apps/sdk";

export async function initTg() {
    if (isTMA()) {
        init();

        if (viewport.mount.isAvailable()) {
            await viewport.mount();
            viewport.expand();
        }

        if (viewport.requestFullscreen.isAvailable()) {
            await viewport.requestFullscreen();
        }
    }
}

export function getInitData() {
    // @ts-expect-error fixme
    return window.Telegram.WebApp.initData;
}