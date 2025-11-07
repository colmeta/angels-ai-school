import { useQuery } from "@tanstack/react-query";

import { apiClient } from "../lib/apiClient";

export interface FeatureFlags {
  enable_parent_chatbot: boolean;
  enable_background_sync: boolean;
  enable_mobile_money_mtn: boolean;
  enable_mobile_money_airtel: boolean;
  enable_student_portal: boolean;
  enable_staff_portal: boolean;
}

export const useFeatureFlags = (schoolId: string) =>
  useQuery({
    queryKey: ["feature-flags", schoolId],
    queryFn: async () => {
      const { data } = await apiClient.get<FeatureFlags>(
        `/schools/${schoolId}/feature-flags`,
      );
      return data;
    },
    staleTime: 1000 * 60 * 60,
  });
