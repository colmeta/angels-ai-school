import { apiClient } from "./apiClient";
export const sendChatMessage = async (schoolId, messages, locale = "en", channel = "parent_app") => {
    const { data } = await apiClient.post("/chatbot/query", {
        school_id: schoolId,
        messages,
        locale,
        channel,
    });
    return data;
};
