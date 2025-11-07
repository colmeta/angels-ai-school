import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { v4 as uuid } from "uuid";

import { useFeatureFlags } from "../hooks/useFeatureFlags";
import { useBrandingStore } from "../stores/branding";
import { useOfflineSync } from "../hooks/useOfflineSync";
import { initiateMobileMoney, listMobileMoneyTransactions, MobileMoneyPayload } from "../lib/payments";
import { sendChatMessage, ChatMessage } from "../lib/chatbot";

type LocalChatEntry = {
  id: string;
  role: "parent" | "assistant";
  message: string;
  status?: "queued" | "sent" | "pending";
  source?: string;
};

const toneClasses = {
  success: "border-emerald-400/40 bg-emerald-500/10 text-emerald-100",
  warning: "border-amber-400/40 bg-amber-500/10 text-amber-100",
  info: "border-blue-400/40 bg-blue-500/10 text-blue-100",
};

export const ParentPortal = () => {
  const schoolId = useBrandingStore((state) => state.schoolId);
  const { data: flags } = useFeatureFlags(schoolId);
  const { tasks, enqueueTask } = useOfflineSync();

  const [chatHistory, setChatHistory] = useState<LocalChatEntry[]>([]);
  const [input, setInput] = useState("");
  const [selectedProvider, setSelectedProvider] = useState<"MTN" | "AIRTEL">("MTN");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [paymentAmount, setPaymentAmount] = useState<number>(120000);
  const [paymentCurrency, setPaymentCurrency] = useState("UGX");
  const [paymentFeedback, setPaymentFeedback] = useState<string | null>(null);

  const pendingPaymentTasks = useMemo(
    () => tasks.filter((task) => task.endpoint === "/payments/mobile-money/initiate"),
    [tasks],
  );

  const transactionsQuery = useQuery({
    queryKey: ["mobile-money-transactions", schoolId],
    queryFn: () => listMobileMoneyTransactions(schoolId),
    enabled: Boolean(schoolId),
  });

  useEffect(() => {
    const handleOnline = () => {
      transactionsQuery.refetch();
    };
    window.addEventListener("online", handleOnline);
    return () => window.removeEventListener("online", handleOnline);
  }, [transactionsQuery]);

  const paymentMutation = useMutation({
    mutationFn: (payload: MobileMoneyPayload) => initiateMobileMoney(payload),
    onSuccess: (data) => {
      setPaymentFeedback(data.instructions?.note ?? "Payment request recorded.");
      transactionsQuery.refetch();
    },
    onError: (error: unknown) => {
      setPaymentFeedback(
        error instanceof Error ? error.message : "Unable to initiate payment right now.",
      );
    },
  });

  const chatMutation = useMutation({
    mutationFn: (messages: ChatMessage[]) => sendChatMessage(schoolId, messages),
    onSuccess: (data) => {
      setChatHistory((prev) => [
        ...prev,
        {
          id: uuid(),
          role: "assistant",
          message: data.response,
          status: "sent",
          source: data.source,
        },
      ]);
    },
    onError: () => {
      setChatHistory((prev) => [
        ...prev,
        {
          id: uuid(),
          role: "assistant",
          message: "We’ll deliver a full answer once we reconnect. Thank you for your patience.",
          status: "pending",
        },
      ]);
    },
  });

  const buildChatMessages = (entries: LocalChatEntry[]): ChatMessage[] =>
    entries.map((entry) => ({
      role: entry.role === "parent" ? "user" : "assistant",
      content: entry.message,
    }));

  const handleSendMessage = () => {
    if (!input.trim()) return;
    const parentMessage: LocalChatEntry = {
      id: uuid(),
      role: "parent",
      message: input.trim(),
      status: navigator.onLine ? "sent" : "queued",
    };

    const nextHistory = [...chatHistory, parentMessage];
    setChatHistory(nextHistory);
    setInput("");

    const payloadMessages = buildChatMessages(nextHistory);

    if (!navigator.onLine) {
      enqueueTask(
        "/chatbot/query",
        {
          school_id: schoolId,
          messages: payloadMessages,
          locale: "en",
          channel: "parent_app",
        },
        "POST",
      );
      setChatHistory((prev) => [
        ...prev,
        {
          id: uuid(),
          role: "assistant",
          message: "Thanks! I’ll sync this question with the team once we’re back online.",
          status: "queued",
        },
      ]);
      return;
    }

    chatMutation.mutate(payloadMessages);
  };

  const handlePayment = () => {
    if (!phoneNumber.trim()) {
      setPaymentFeedback("Enter the mobile number that will make the payment.");
      return;
    }
    const payload: MobileMoneyPayload = {
      school_id: schoolId,
      provider: selectedProvider,
      amount: paymentAmount,
      currency: paymentCurrency,
      phone_number: phoneNumber,
      initiated_by: "parent_app",
    };

    if (!navigator.onLine) {
      enqueueTask("/payments/mobile-money/initiate", payload, "POST");
      setPaymentFeedback(
        "Payment request saved. We’ll process it automatically when you reconnect.",
      );
      return;
    }

    paymentMutation.mutate(payload);
  };

  const transactions = transactionsQuery.data ?? [];

  return (
    <section className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-2xl font-semibold">Parent Engagement Hub</h1>
        <p className="text-slate-300">
          Check attendance, health alerts, fee balances, pay by mobile money, and chat with the AI
          concierge. No WhatsApp bots—everything lives inside this app and works offline.
        </p>
      </header>

      <div className="grid gap-4 md:grid-cols-3">
        <InfoCard title="Today’s Attendance" value="Present" tone="success" />
        <InfoCard title="Fee Balance" value="UGX 120,000" tone="warning" />
        <InfoCard title="Health Updates" value="Cleared for sports" tone="info" />
      </div>

      <div className="rounded-3xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
        <div className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
          <div>
            <h2 className="text-xl font-semibold">Pay School Fees via Mobile Money</h2>
            <p className="text-sm text-slate-300">
              Supports MTN Mobile Money and Airtel Money. Requests queue offline and sync when
              you’re connected again.
            </p>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-4">
          <div className="flex flex-col gap-2">
            <label className="text-xs uppercase tracking-wide text-slate-400">Provider</label>
            <select
              value={selectedProvider}
              onChange={(event) => setSelectedProvider(event.target.value as "MTN" | "AIRTEL")}
              className="rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
            >
              <option value="MTN">MTN Mobile Money</option>
              <option value="AIRTEL">Airtel Money</option>
            </select>
          </div>
          <div className="flex flex-col gap-2">
            <label className="text-xs uppercase tracking-wide text-slate-400">Amount</label>
            <input
              type="number"
              min={1000}
              value={paymentAmount}
              onChange={(event) => setPaymentAmount(Number(event.target.value))}
              className="rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
            />
          </div>
          <div className="flex flex-col gap-2">
            <label className="text-xs uppercase tracking-wide text-slate-400">Currency</label>
            <input
              value={paymentCurrency}
              onChange={(event) => setPaymentCurrency(event.target.value.toUpperCase())}
              className="rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
            />
          </div>
          <div className="flex flex-col gap-2">
            <label className="text-xs uppercase tracking-wide text-slate-400">Phone Number</label>
            <input
              value={phoneNumber}
              onChange={(event) => setPhoneNumber(event.target.value)}
              placeholder="+2567XXXXXXXX"
              className="rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
            />
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={handlePayment}
            className="rounded-full bg-emerald-500 px-5 py-2 text-sm font-semibold text-black hover:bg-emerald-400"
            disabled={paymentMutation.isLoading}
          >
            {navigator.onLine ? "Send Payment Request" : "Queue Payment Request"}
          </button>
          {paymentFeedback && <span className="text-sm text-slate-300">{paymentFeedback}</span>}
        </div>

        {pendingPaymentTasks.length > 0 && (
          <div className="rounded-2xl border border-amber-400/40 bg-amber-500/10 p-4 text-xs text-amber-100">
            <p className="font-semibold uppercase tracking-wide">Pending offline requests</p>
            <ul className="mt-2 space-y-1">
              {pendingPaymentTasks.map((task) => (
                <li key={task.id}>
                  • {task.payload?.provider ?? "Provider"} — {task.payload?.amount ?? ""}{" "}
                  {task.payload?.currency ?? ""}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {flags?.enable_parent_chatbot && (
        <div className="rounded-3xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
          <h2 className="text-xl font-semibold">Parent Chat Assistant</h2>
          <div className="h-60 overflow-y-auto space-y-3 rounded-2xl bg-slate-950/60 p-4 text-sm">
            {chatHistory.length === 0 && (
              <p className="text-slate-400">
                Ask about fees, attendance, school events, or request documents. Responses are
                instant offline and enriched once Clarity syncs.
              </p>
            )}
            {chatHistory.map((entry) => (
              <div
                key={entry.id}
                className={`max-w-xs rounded-2xl px-3 py-2 ${
                  entry.role === "assistant"
                    ? "bg-slate-800 text-slate-200"
                    : "ml-auto bg-blue-600 text-white"
                }`}
              >
                <p>{entry.message}</p>
                {entry.status === "queued" && (
                  <p className="mt-1 text-[10px] uppercase tracking-wide text-slate-300">
                    queued for sync
                  </p>
                )}
                {entry.source && (
                  <p className="mt-1 text-[10px] uppercase tracking-wide text-slate-300">
                    source: {entry.source}
                  </p>
                )}
              </div>
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
              onClick={handleSendMessage}
              className="rounded-full bg-blue-600 px-5 py-2 text-sm font-semibold hover:bg-blue-500"
            >
              {navigator.onLine ? "Send" : "Queue"}
            </button>
          </div>
        </div>
      )}

      <div className="rounded-3xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
        <h2 className="text-xl font-semibold">Recent Mobile Money Transactions</h2>
        {transactions.length === 0 ? (
          <p className="text-sm text-slate-400">No transactions yet. Start by submitting a fee payment.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-800 text-sm">
              <thead className="text-left uppercase tracking-wide text-xs text-slate-400">
                <tr>
                  <th className="px-3 py-2">Reference</th>
                  <th className="px-3 py-2">Provider</th>
                  <th className="px-3 py-2">Amount</th>
                  <th className="px-3 py-2">Status</th>
                  <th className="px-3 py-2">Notes</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {transactions.map((txn: any) => (
                  <tr key={txn.reference}>
                    <td className="px-3 py-2 font-mono text-xs text-slate-300">{txn.reference}</td>
                    <td className="px-3 py-2">{txn.provider}</td>
                    <td className="px-3 py-2">
                      {txn.currency} {txn.amount}
                    </td>
                    <td className="px-3 py-2 capitalize">
                      <StatusBadge status={txn.status} />
                    </td>
                    <td className="px-3 py-2 text-slate-400 text-xs">
                      {txn.message || txn.metadata?.note || "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );
};

interface InfoCardProps {
  title: string;
  value: string;
  tone: "success" | "warning" | "info";
}

const InfoCard = ({ title, value, tone }: InfoCardProps) => (
  <div className={`rounded-2xl border px-5 py-4 ${toneClasses[tone]}`}>
    <p className="text-xs uppercase tracking-wide opacity-80">{title}</p>
    <p className="text-xl font-semibold mt-2">{value}</p>
  </div>
);

const StatusBadge = ({ status }: { status: string }) => {
  const tone =
    status === "success"
      ? "bg-emerald-500/20 text-emerald-100"
      : status === "failed"
      ? "bg-rose-500/20 text-rose-100"
      : "bg-blue-500/20 text-blue-100";
  return (
    <span className={`rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-wide ${tone}`}>
      {status ?? "pending"}
    </span>
  );
};
