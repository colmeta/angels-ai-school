/**
 * Smart Entry Service
 * ===================
 * Bridges the Frontend "Magic Box" input to the Backend "Command Intelligence" Agent.
 * Replaces previous client-side regex mocks with real NLP.
 */
import { localAgent } from "./LocalAgentService";
import { apiClient } from "../lib/apiClient";
export const SmartEntryService = {
    /**
     * Sends natural language command to the backend AI agent.
     * With Edge AI fallback for offline/low-latency usage.
     */
    parse: async (input, schoolId) => {
        // 1. Try Local Edge AI if ready
        if (localAgent.getStatus() === 'ready') {
            try {
                console.log("[SmartEntry] Using Local Edge AI Core...");
                const localResult = await localAgent.parse(input);
                return {
                    action: localResult.action || "unknown",
                    entity: localResult.entity || "unknown",
                    data: localResult.data || localResult,
                    confidence: 1.0 // Local is deterministic once parsed
                };
            }
            catch (e) {
                console.warn("[SmartEntry] Local AI failed, falling back...", e);
            }
        }
        // 2. Fallback to Cloud AI if online
        if (navigator.onLine) {
            try {
                const response = await apiClient.post(`/agents/command`, {
                    command: input,
                    school_id: schoolId,
                    user_role: "admin"
                });
                if (response.data && response.data.parsed) {
                    return response.data.parsed;
                }
            }
            catch (error) {
                console.error("SmartEntry Cloud AI Error:", error);
            }
        }
        // 3. Final Fallback (Unknown)
        return {
            action: "unknown",
            entity: "unknown",
            data: {},
            confidence: 0
        };
    },
    /**
     * Executes the parsed command after user confirmation.
     */
    execute: async (command, schoolId) => {
        // In a perfect world, the backend agent executes it.
        // For safety, the UI often confirms then sends an 'abuse' or 'confirm' signal.
        // For this implementation, we assume the 'parse' step was just a preview,
        // and we might need a separate 'execute' endpoint or the parse already did it?
        // Use Case: The user types "Add student", sees the preview form filled, then clicks "Save".
        // In that case, the UI takes the 'data' from parse() and calls the standard API (e.g. useStudentStore.add).
        // This method helps if we want "Zero-Click" execution.
        return apiClient.post(`/agents/execute-command`, {
            command: command,
            school_id: schoolId
        });
    }
};
