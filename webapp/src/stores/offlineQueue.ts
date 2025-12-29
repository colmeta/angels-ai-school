import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface OfflineTask {
  id: string;
  endpoint: string;
  payload: unknown;
  method: "POST" | "PUT" | "PATCH" | "DELETE";
  createdAt: string;
}

interface OfflineQueueState {
  tasks: OfflineTask[];
  enqueue: (task: OfflineTask) => void;
  dequeue: (id: string) => void;
  clear: () => void;
}

export const useOfflineQueue = create<OfflineQueueState>()(
  persist(
    (set, get) => ({
      tasks: [],
      enqueue: (task) =>
        set({
          tasks: [...get().tasks, task],
        }),
      dequeue: (id) =>
        set({
          tasks: get().tasks.filter((task) => task.id !== id),
        }),
      clear: () => set({ tasks: [] }),
    }),
    {
      name: "offline-task-queue",
    },
  ),
);
