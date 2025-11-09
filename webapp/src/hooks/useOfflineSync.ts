import { useEffect } from "react";
import { v4 as uuid } from "uuid";

import { apiClient } from "../lib/apiClient";
import { useOfflineQueue } from "../stores/offlineQueue";

export const useOfflineSync = () => {
  const { tasks, dequeue, clear } = useOfflineQueue();

  useEffect(() => {
    if (!("serviceWorker" in navigator) || !navigator.serviceWorker) return;

    const handleMessage = (event: MessageEvent) => {
      if (event.data?.type === "SYNC_REQUEST") {
        processQueue();
      }
    };

    navigator.serviceWorker.addEventListener("message", handleMessage);
    return () => navigator.serviceWorker.removeEventListener("message", handleMessage);
  }, [tasks]);

  const processQueue = async () => {
    if (!navigator.onLine) return;
    for (const task of tasks) {
      try {
        await apiClient.request({
          url: task.endpoint,
          method: task.method,
          data: task.payload,
        });
        dequeue(task.id);
      } catch (error) {
        console.error("Failed to sync task", task.id, error);
      }
    }
  };

  const enqueueTask = (endpoint: string, payload: unknown, method: "POST" | "PUT" | "PATCH" | "DELETE") => {
    useOfflineQueue.getState().enqueue({
      id: uuid(),
      endpoint,
      payload,
      method,
      createdAt: new Date().toISOString(),
    });
    requestBackgroundSync();
  };

  const requestBackgroundSync = async () => {
    if ("serviceWorker" in navigator && "SyncManager" in window) {
      const registration = await navigator.serviceWorker.ready;
      try {
        await (registration as any).sync.register("sync-offline-queue");
      } catch (error) {
        console.error("Background sync registration failed", error);
        processQueue();
      }
    } else {
      processQueue();
    }
  };

  return { tasks, enqueueTask, clearQueue: clear, processQueue };
};
