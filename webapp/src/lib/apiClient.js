import axios from "axios";
const apiBase = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api";
export const apiClient = axios.create({
    baseURL: apiBase,
    timeout: 20000,
    headers: {
        "Content-Type": "application/json",
    },
});
export const clarityClient = axios.create({
    baseURL: `${apiBase}/clarity`,
    timeout: 60000,
    headers: {
        "Content-Type": "application/json",
    },
});
