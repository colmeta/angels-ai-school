import { apiClient } from "./apiClient";

export interface MobileMoneyPayload {
  school_id: string;
  provider: "MTN" | "AIRTEL";
  amount: number;
  currency?: string;
  phone_number: string;
  student_id?: string | null;
  student_fee_id?: string | null;
  metadata?: Record<string, unknown>;
  initiated_by?: string;
}

export const initiateMobileMoney = async (payload: MobileMoneyPayload) => {
  const { data } = await apiClient.post("/payments/mobile-money/initiate", payload);
  return data;
};

export const listMobileMoneyTransactions = async (schoolId: string) => {
  const { data } = await apiClient.get("/payments/mobile-money/transactions", {
    params: { school_id: schoolId, limit: 25 },
  });
  return data.transactions;
};
