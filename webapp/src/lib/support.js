import { apiClient } from "./apiClient";
export const logIncident = async (schoolId, payload) => {
    const { data } = await apiClient.post(`/support/${schoolId}/incidents`, payload);
    return data;
};
export const fetchIncidents = async (schoolId) => {
    const { data } = await apiClient.get(`/support/${schoolId}/incidents`);
    return data.incidents;
};
export const adjustInventory = async (schoolId, payload) => {
    const { data } = await apiClient.post(`/support/${schoolId}/inventory/adjust`, payload);
    return data;
};
export const fetchInventorySnapshot = async (schoolId) => {
    const { data } = await apiClient.get(`/support/${schoolId}/inventory`);
    return data;
};
export const createHealthVisit = async (schoolId, payload) => {
    const { data } = await apiClient.post(`/support/${schoolId}/health`, payload);
    return data;
};
export const fetchHealthVisits = async (schoolId) => {
    const { data } = await apiClient.get(`/support/${schoolId}/health`);
    return data.visits;
};
export const recordLibraryTransaction = async (schoolId, payload) => {
    const { data } = await apiClient.post(`/support/${schoolId}/library`, payload);
    return data;
};
export const fetchLibraryTransactions = async (schoolId) => {
    const { data } = await apiClient.get(`/support/${schoolId}/library`);
    return data.transactions;
};
export const recordTransportEvent = async (schoolId, payload) => {
    const { data } = await apiClient.post(`/support/${schoolId}/transport`, payload);
    return data;
};
export const fetchTransportEvents = async (schoolId) => {
    const { data } = await apiClient.get(`/support/${schoolId}/transport`);
    return data.events;
};
export const fetchSupportReport = async (schoolId) => {
    const { data } = await apiClient.get(`/support/${schoolId}/report`);
    return data;
};
