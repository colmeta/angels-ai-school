import axios from "axios";

const apiBase = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";

export const apiClient = axios.create({
  baseURL: apiBase,
  timeout: 20_000,
  headers: {
    "Content-Type": "application/json",
  },
});

export const clarityClient = axios.create({
  baseURL: `${apiBase}/clarity`,
  timeout: 60_000,
  headers: {
    "Content-Type": "application/json",
  },
});
