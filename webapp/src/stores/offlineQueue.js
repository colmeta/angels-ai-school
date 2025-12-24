import { create } from "zustand";
import { persist } from "zustand/middleware";
export const useOfflineQueue = create()(persist((set, get) => ({
    tasks: [],
    enqueue: (task) => set({
        tasks: [...get().tasks, task],
    }),
    dequeue: (id) => set({
        tasks: get().tasks.filter((task) => task.id !== id),
    }),
    clear: () => set({ tasks: [] }),
}), {
    name: "offline-task-queue",
}));
