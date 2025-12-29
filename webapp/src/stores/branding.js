import { create } from "zustand";
export const useBrandingStore = create((set) => ({
    schoolId: "default-school",
    displayName: "Angels AI School",
    primaryColor: "#0B69FF",
    accentColor: "#FFB400",
    logoUrl: null,
    setBranding: (payload) => set((state) => ({ ...state, ...payload })),
}));
