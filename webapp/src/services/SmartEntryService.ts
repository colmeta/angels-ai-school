/**
 * Smart Entry Service
 * ===================
 * Bridges the Frontend "Magic Box" input to the Backend "Command Intelligence" Agent.
 * Replaces previous client-side regex mocks with real NLP.
 */
import { apiClient } from "../lib/apiClient";

export interface ParsedCommand {
    action: string;
    entity: string;
    data: any;
    confidence: number;
}

export const SmartEntryService = {
    /**
     * Sends natural language command to the backend AI agent.
     * @param input Natural language string (e.g., "Add student John Doe")
     * @param schoolId The school context ID
     */
    parse: async (input: string, schoolId: string): Promise<ParsedCommand> => {
        try {
            // Call the Backend Command Intelligence Agent
            const response = await apiClient.post(`/agents/command`, {
                command: input,
                school_id: schoolId,
                user_role: "admin" // Context aware in future
            });

            if (response.data && response.data.parsed) {
                return response.data.parsed;
            }

            // Fallback if backend returns generic success but no structured parse
            return {
                action: "unknown",
                entity: "unknown",
                data: {},
                confidence: 0
            };

        } catch (error) {
            console.error("SmartEntry AI Error:", error);
            throw new Error("Failed to process command. The AI agent might be offline.");
        }
    },

    /**
     * Executes the parsed command after user confirmation.
     */
    execute: async (command: ParsedCommand, schoolId: string) => {
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
