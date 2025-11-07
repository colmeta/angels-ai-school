import { apiClient } from "./apiClient";

export interface IncidentRequest {
  category: string;
  description: string;
  severity: string;
  reported_by: string;
  status?: string;
  occurred_at?: string | null;
  metadata?: Record<string, unknown>;
}

export interface InventoryAdjustmentRequest {
  item_name: string;
  change_quantity: number;
  unit?: string;
  reason: string;
  recorded_by: string;
  metadata?: Record<string, unknown>;
}

export interface HealthVisitRequest {
  student_name: string;
  grade?: string;
  symptoms: string;
  action_taken: string;
  guardian_contacted?: string;
  recorded_by: string;
  metadata?: Record<string, unknown>;
}

export interface LibraryTransactionRequest {
  student_name: string;
  class_name?: string;
  book_title: string;
  action: "borrow" | "return";
  due_date?: string;
  recorded_by: string;
  metadata?: Record<string, unknown>;
}

export interface TransportEventRequest {
  route_name: string;
  vehicle?: string;
  status: string;
  notes?: string;
  recorded_by: string;
  event_time?: string;
  metadata?: Record<string, unknown>;
}

export const logIncident = async (schoolId: string, payload: IncidentRequest) => {
  const { data } = await apiClient.post(`/support/${schoolId}/incidents`, payload);
  return data;
};

export const fetchIncidents = async (schoolId: string) => {
  const { data } = await apiClient.get(`/support/${schoolId}/incidents`);
  return data.incidents;
};

export const adjustInventory = async (schoolId: string, payload: InventoryAdjustmentRequest) => {
  const { data } = await apiClient.post(`/support/${schoolId}/inventory/adjust`, payload);
  return data;
};

export const fetchInventorySnapshot = async (schoolId: string) => {
  const { data } = await apiClient.get(`/support/${schoolId}/inventory`);
  return data;
};

export const createHealthVisit = async (schoolId: string, payload: HealthVisitRequest) => {
  const { data } = await apiClient.post(`/support/${schoolId}/health`, payload);
  return data;
};

export const fetchHealthVisits = async (schoolId: string) => {
  const { data } = await apiClient.get(`/support/${schoolId}/health`);
  return data.visits;
};

export const recordLibraryTransaction = async (
  schoolId: string,
  payload: LibraryTransactionRequest,
) => {
  const { data } = await apiClient.post(`/support/${schoolId}/library`, payload);
  return data;
};

export const fetchLibraryTransactions = async (schoolId: string) => {
  const { data } = await apiClient.get(`/support/${schoolId}/library`);
  return data.transactions;
};

export const recordTransportEvent = async (schoolId: string, payload: TransportEventRequest) => {
  const { data } = await apiClient.post(`/support/${schoolId}/transport`, payload);
  return data;
};

export const fetchTransportEvents = async (schoolId: string) => {
  const { data } = await apiClient.get(`/support/${schoolId}/transport`);
  return data.events;
};

export const fetchSupportReport = async (schoolId: string) => {
  const { data } = await apiClient.get(`/support/${schoolId}/report`);
  return data;
};
