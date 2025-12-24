import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../lib/apiClient";
export const useFeatureFlags = (schoolId) => useQuery({
    queryKey: ["feature-flags", schoolId],
    queryFn: async () => {
        const { data } = await apiClient.get(`/schools/${schoolId}/feature-flags`);
        return data;
    },
    staleTime: 1000 * 60 * 60,
});
