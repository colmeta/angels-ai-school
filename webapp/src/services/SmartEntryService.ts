
export interface SmartEntryResult {
    present: string[];
    absent: string[];
    action: 'attendance' | 'grades' | 'unknown';
    confidence: number;
    summary: string;
}

export const SmartEntryService = {
    /**
     * Mocks an NLP parser that takes natural language and returns structured data.
     * In the real app, this would call the Python 'Clarity Engine'.
     */
    parseNaturalLanguageEntry: async (input: string, allStudents: string[]): Promise<SmartEntryResult> => {
        // Simulate network delay for "AI Processing" feel
        await new Promise(resolve => setTimeout(resolve, 1500));

        const lowerInput = input.toLowerCase();

        // 1. Attendance Logic
        if (lowerInput.includes('present') || lowerInput.includes('absent') || lowerInput.includes('came') || lowerInput.includes('missed')) {
            const absentNames: string[] = [];
            const presentNames: string[] = [];

            // Heuristic: "Everyone is present except X, Y"
            if (lowerInput.includes('except')) {
                // Find names after "except"
                // This is a naive mock implementation
                allStudents.forEach(student => {
                    if (lowerInput.includes(student.toLowerCase())) {
                        absentNames.push(student);
                    } else {
                        presentNames.push(student);
                    }
                });

                return {
                    action: 'attendance',
                    present: presentNames,
                    absent: absentNames,
                    confidence: 0.95,
                    summary: `Marked ${presentNames.length} students present and ${absentNames.length} absent.`
                };
            }

            // Heuristic: "Mark X, Y, Z as absent"
            if (lowerInput.includes('absent')) {
                allStudents.forEach(student => {
                    if (lowerInput.includes(student.toLowerCase())) {
                        absentNames.push(student);
                    } else {
                        presentNames.push(student); // Default to present if not mentioned as absent
                    }
                });
                return {
                    action: 'attendance',
                    present: presentNames,
                    absent: absentNames,
                    confidence: 0.92,
                    summary: `Marked ${absentNames.join(', ')} as absent.`
                };
            }
        }

        return {
            present: [],
            absent: [],
            action: 'unknown',
            confidence: 0.0,
            summary: "I didn't quite catch that. Try saying 'Everyone is present except John'."
        };
    }
};
