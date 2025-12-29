import { apiClient } from "../lib/apiClient";
import { setAIMode } from "../config/aiConfig";

/**
 * Experiment Service
 * Handles fetching A/B test variants and applying them
 */
export const ExperimentService = {
    /**
     * Fetch user's assigned variant for AI mode experiment
     */
    async enrollInAIModeExperiment(userId: string) {
        try {
            // Check if already enrolled
            if (localStorage.getItem('ab_test_ai_mode')) return;

            const response = await apiClient.post("/v1/experiments/get-variant", {
                experiment_name: "ai_tier_distribution",
                user_id: parseInt(userId.replace(/\D/g, '').slice(0, 9)) || 1
            });

            if (response.data.success && response.data.variant) {
                const variant = response.data.variant;
                // Map variants to AI modes
                let mode: 'core' | 'hybrid' | 'flash' = 'hybrid';
                if (variant === 'variant_a') mode = 'core';
                if (variant === 'variant_b') mode = 'hybrid';
                if (variant === 'variant_c') mode = 'flash';

                localStorage.setItem('ab_test_ai_mode', mode);
                console.log(`[A/B Test] Enrolled in ${mode} mode`);
            }
        } catch (error) {
            console.error("[A/B Test] Failed to enroll:", error);
        }
    }
};
