import { create } from "zustand";

interface BrandingState {
  schoolId: string;
  displayName: string;
  primaryColor: string;
  accentColor: string;
  logoUrl?: string | null;
  setBranding: (payload: Partial<BrandingState>) => void;
}

export const useBrandingStore = create<BrandingState>((set) => ({
  schoolId: "default-school",
  displayName: "Angels AI School",
  primaryColor: "#0B69FF",
  accentColor: "#FFB400",
  logoUrl: null,
  setBranding: (payload) => set((state) => ({ ...state, ...payload })),
}));
