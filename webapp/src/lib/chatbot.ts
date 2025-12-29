import { apiClient } from "./apiClient";

export interface ChatMessage {
  role: "user" | "assistant" | "system" | "parent";
  content: string;
}

interface ChatbotResponse {
  success: boolean;
  response: string;
  source: string;
}

export const sendChatMessage = async (
  schoolId: string,
  messages: ChatMessage[],
  locale = "en",
  channel = "parent_app",
): Promise<ChatbotResponse> => {
  const { data } = await apiClient.post("/chatbot/query", {
    school_id: schoolId,
    messages,
    locale,
    channel,
  });
  return data;
};
