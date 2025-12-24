/* eslint-disable no-console */
import { Workbox } from "workbox-window";
export const registerSW = () => {
    if ("serviceWorker" in navigator) {
        const wb = new Workbox("/sw.js");
        wb.addEventListener("waiting", () => {
            wb.messageSkipWaiting();
        });
        wb.addEventListener("controlling", () => {
            window.location.reload();
        });
        wb.register()
            .then(() => console.info("🛠️ Service worker registered"))
            .catch((err) => console.error("⚠️ Service worker registration failed", err));
    }
};
