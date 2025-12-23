import React from "react";
import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";

import App from "./App";
import "./index.css";
import { registerSW } from "./serviceWorkerRegistration";
import { GoogleOAuthProvider } from "@react-oauth/google";
import { ErrorBoundary } from "./components/ErrorBoundary";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      refetchOnWindowFocus: false,
      staleTime: 1000 * 60,
    },
  },
});

registerSW();

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <GoogleOAuthProvider clientId={import.meta.env.VITE_GOOGLE_CLIENT_ID || ""}>
          <ErrorBoundary>
            <App />
          </ErrorBoundary>
        </GoogleOAuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>,
);
