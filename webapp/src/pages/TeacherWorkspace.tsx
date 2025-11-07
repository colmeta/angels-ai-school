import { useState } from "react";
import dayjs from "dayjs";

import { useOfflineSync } from "../hooks/useOfflineSync";

export const TeacherWorkspace = () => {
  const { enqueueTask, tasks } = useOfflineSync();
  const [lastCaptured, setLastCaptured] = useState<string | null>(null);

  const handleCapture = async (type: "attendance" | "marks") => {
    const fakePayload = {
      type,
      capturedAt: new Date().toISOString(),
      notes: `${type} sheet uploaded`,
    };
    enqueueTask("/teacher/uploads", fakePayload, "POST");
    setLastCaptured(`${type} at ${dayjs().format("HH:mm")}`);
  };

  const pendingCount = tasks.length;

  return (
    <section className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-2xl font-semibold">Teacher Control Hub</h1>
        <p className="text-slate-300">
          Snap attendance, capture assessment sheets, and command AI to prepare reports—everything
          works offline and syncs automatically.
        </p>
      </header>

      <div className="grid gap-4 md:grid-cols-2">
        <button
          className="rounded-2xl border border-slate-800 bg-slate-900/70 px-6 py-5 text-left transition hover:border-slate-700 hover:bg-slate-800"
          onClick={() => handleCapture("attendance")}
        >
          <h2 className="text-xl font-semibold mb-1">Capture Attendance Sheet</h2>
          <p className="text-sm text-slate-300">
            Take a photo of your attendance register. AI will digitize and notify parents instantly.
          </p>
        </button>

        <button
          className="rounded-2xl border border-slate-800 bg-slate-900/70 px-6 py-5 text-left transition hover:border-slate-700 hover:bg-slate-800"
          onClick={() => handleCapture("marks")}
        >
          <h2 className="text-xl font-semibold mb-1">Capture Assessment Marks</h2>
          <p className="text-sm text-slate-300">
            Snap exam results; Clarity will distribute grades to student profiles and parent portals.
          </p>
        </button>
      </div>

      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
        <h3 className="text-lg font-semibold mb-2">AI Commands</h3>
        <ul className="space-y-2 text-sm text-slate-300">
          <li>• “Generate weekly parent report for Primary Five.”</li>
          <li>• “Summarize attendance anomalies for Grade 7 this week.”</li>
          <li>• “Prepare revision plan for students below 65% in Mathematics.”</li>
        </ul>
      </div>

      <footer className="rounded-2xl border border-slate-800 bg-slate-900/50 px-6 py-4 text-sm text-slate-300">
        <p>
          Pending uploads: <span className="font-semibold text-slate-50">{pendingCount}</span>
        </p>
        {lastCaptured && <p>Last captured: {lastCaptured}</p>}
        <p>Once you reconnect, a full report is delivered to leadership automatically.</p>
      </footer>
    </section>
  );
};
