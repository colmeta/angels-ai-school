import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../lib/apiClient";
import { useBrandingStore } from "../stores/branding";
export const useBranding = (schoolId) => {
    const setBranding = useBrandingStore((state) => state.setBranding);
    return useQuery({
        queryKey: ["branding", schoolId],
        queryFn: async () => {
            const { data } = await apiClient.get(`/schools/${schoolId}/branding`);
            setBranding({
                schoolId: data.school_id,
                displayName: data.display_name || "Angels AI School",
                primaryColor: data.primary_color,
                accentColor: data.accent_color,
                logoUrl: data.logo_url,
            });
            return data;
        },
        staleTime: 1000 * 60 * 60,
    });
};
