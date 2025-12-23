import { useQuery } from "@tanstack/react-query";

import { apiClient } from "../lib/apiClient";
import { useBrandingStore } from "../stores/branding";

interface BrandingResponse {
  school_id: string;
  display_name: string;
  primary_color: string;
  accent_color: string;
  logo_url?: string | null;
}

export const useBranding = (schoolId: string) => {
  const setBranding = useBrandingStore((state) => state.setBranding);

  return useQuery({
    queryKey: ["branding", schoolId],
    queryFn: async () => {
      const { data } = await apiClient.get<BrandingResponse>(`/schools/${schoolId}/branding`);
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
