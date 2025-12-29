import { jsx as _jsx } from "react/jsx-runtime";
import { useEffect, useState } from "react";
export const OfflineBanner = () => {
    const [isOffline, setIsOffline] = useState(!navigator.onLine);
    useEffect(() => {
        const handleOnline = () => setIsOffline(false);
        const handleOffline = () => setIsOffline(true);
        window.addEventListener("online", handleOnline);
        window.addEventListener("offline", handleOffline);
        return () => {
            window.removeEventListener("online", handleOnline);
            window.removeEventListener("offline", handleOffline);
        };
    }, []);
    if (!isOffline)
        return null;
    return (_jsx("div", { className: "bg-amber-500 text-black px-4 py-2 text-sm font-semibold text-center", children: "You are offline. All actions are saved and will sync automatically once connectivity returns." }));
};
