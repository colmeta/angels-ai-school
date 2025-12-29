import { apiClient } from "./apiClient";
export const initiateMobileMoney = async (payload) => {
    const { data } = await apiClient.post("/payments/mobile-money/initiate", payload);
    return data;
};
export const listMobileMoneyTransactions = async (schoolId) => {
    const { data } = await apiClient.get("/payments/mobile-money/transactions", {
        params: { school_id: schoolId, limit: 25 },
    });
    return data.transactions;
};
