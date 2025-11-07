import { useState } from "react";

import { useFeatureFlags } from "../hooks/useFeatureFlags";
import { useBrandingStore } from "../stores/branding";

export const ParentPortal = () => {
  const schoolId = useBrandingStore((state) => state.schoolId);
  const { data: flags } = useFeatureFlags(schoolId);
  const [chatHistory, setChatHistory] = useState<
    { role: "parent" | "assistant"; message: string }[]
  >([]);
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (!input.trim()) return;
    setChatHistory((prev) => [...prev, { role: "parent", message: input }]);
    setChatHistory((prev) => [
      ...prev,
      {
        role: "assistant",
        message:
          "Thank you! I have recorded your question and will sync with the Clarity engine when online.",
      },
    ]);
    setInput("");
  };

  return (
    <section className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-2xl font-semibold">Parent Engagement Hub</h1>
        <p className="text-slate-300">
          Check attendance, health alerts, fee balances, and chat with the AI concierge. No WhatsApp
          fees—everything lives inside this app.
        </p>
      </header>

      <div className="grid gap-4 md:grid-cols-3">
        <InfoCard title="Today’s Attendance" value="Present" tone="success" />
        <InfoCard title="Fee Balance" value="UGX 120,000" tone="warning" />
        <InfoCard title="Health Updates" value="Cleared for sports" tone="info" />
      </div>

      {flags?.enable_parent_chatbot && (
        <div className="rounded-3xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
          <h2 className="text-xl font-semibold">Parent Chat Assistant</h2>
          <div className="h-60 overflow-y-auto space-y-3 rounded-2xl bg-slate-950/60 p-4 text-sm">
            {chatHistory.length === 0 && (
              <p className="text-slate-400">
                Ask about fees, attendance, school events, or request documents. Responses are
                instant offline, and enriched once Clarity syncs.
              </p>
            )}
            {chatHistory.map((entry, index) => (
              <p
                key={index}
                className={`rounded-2xl px-3 py-2 ${
                  entry.role === "assistant"
                    ? "bg-slate-800 text-slate-200 self-start"
                    : "bg-blue-600 text-white ml-auto max-w-xs"
                }`}
              >
                {entry.message}
              </p>
            ))}
          </div>
          <div className="flex gap-2">
            <input
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Ask about fees, events, attendance…"
              className="flex-1 rounded-full border border-slate-700 bg-slate-900 px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={handleSend}
              className="rounded-full bg-blue-600 px-5 py-2 text-sm font-semibold hover:bg-blue-500"
            >
              Send
            </button>
          </div>
        </div>
      )}

      <div className="rounded-3xl border border-slate-800 bg-slate-900/60 p-6">
        <h2 className="text-xl font-semibold mb-4">Mobile Money Support</h2>
        <ul className="space-y-2 text-sm text-slate-300">
          <li>• MTN Mobile Money (dial *165#) — select “School Fees” → “Angels AI School”.</li>
          <li>• Airtel Money (dial *185#) — choose “Pay Bills” → “Education” → “Angels AI School”.</li>
          <li>• All payments sync instantly when online; receipts stored in your timeline.</li>
        </ul>
      </div>
    </section>
  );
};

interface InfoCardProps {
  title: string;
  value: string;
  tone: "success" | "warning" | "info";
}

const toneClasses = {
  success: "border-emerald-400/40 bg-emerald-500/10 text-emerald-100",
  warning: "border-amber-400/40 bg-amber-500/10 text-amber-100",
  info: "border-blue-400/40 bg-blue-500/10 text-blue-100",
};

const InfoCard = ({ title, value, tone }: InfoCardProps) => (
  <div className={`rounded-2xl border px-5 py-4 ${toneClasses[tone]}`}>
    <p className="text-xs uppercase tracking-wide opacity-80">{title}</p>
    <p className="text-xl font-semibold mt-2">{value}</p>
  </div>
);
