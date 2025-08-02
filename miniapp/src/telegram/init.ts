import { viewport, init, isTMA } from "@telegram-apps/sdk";

export async function initTg() {
    if (isTMA()) {
        init();

        if (viewport.mount.isAvailable()) {
            await viewport.mount();
            viewport.expand();
        }

        // Request fullscreen only if on a mobile device
        // const isMobile = /Mobi|Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
        // if (isMobile && viewport.requestFullscreen.isAvailable()) {
        //     await viewport.requestFullscreen();
        // }
    }
}

export function getInitData() {
    return window.Telegram.WebApp.initData;
}