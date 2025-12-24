/**
 * PRODUCTION Parent Portal - Complete PWA for Parents
 * - Real notifications with full access to child data
 * - All reports: attendance, grades, health, fees, incidents
 * - AI chatbot (no WhatsApp costs)
 * - Mobile money payments (MTN + Airtel)
 * - Offline-first with background sync
 * - Installable on any device
 */
import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { v4 as uuid } from "uuid";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";

dayjs.extend(relativeTime);

import { useFeatureFlags } from "../hooks/useFeatureFlags";
import { useBrandingStore } from "../stores/branding";
import { useOfflineSync } from "../hooks/useOfflineSync";
import { initiateMobileMoney, MobileMoneyPayload } from "../lib/payments";
import { apiClient } from "../lib/apiClient";
import BriefingWidget from "../components/Dashboard/BriefingWidget";
import CalendarHub from "./parent/CalendarHub";

interface Child {
  id: string;
  first_name: string;
  last_name: string;
  class_name: string;
  admission_number: string;
}

interface Notification {
  id: string;
  notification_type: string;
  title: string;
  message: string;
  priority: string;
  is_read: boolean;
  created_at: string;
  related_entity_type?: string;
  related_entity_id?: string;
}

interface ChildReport {
  attendance: Array<{ date: string; status: string; notes?: string }>;
  recent_results: Array<{
    name: string;
    subject: string;
    date: string;
    max_marks: number;
    marks_obtained: number;
    grade: string;
  }>;
  health_visits: Array<{
    visit_date: string;
    symptoms: string;
    diagnosis?: string;
    treatment?: string;
  }>;
  fees: Array<{
    name: string;
    amount_due: number;
    amount_paid: number;
    balance: number;
    status: string;
    due_date: string;
  }>;
}

type LocalChatEntry = {
  id: string;
  role: "parent" | "assistant";
  message: string;
  status?: "queued" | "sent" | "pending";
  source?: string;
};

export const ParentPortal = () => {
  const schoolId = useBrandingStore((state) => state.schoolId) || "demo-school";
  const parentId = localStorage.getItem("parent_id") || "demo-parent";
  const { data: flags } = useFeatureFlags(schoolId);
  const { tasks, enqueueTask } = useOfflineSync();

  const [activeTab, setActiveTab] = useState<"dashboard" | "notifications" | "reports" | "payments" | "chat" | "calendar">("dashboard");
  const [selectedChildId, setSelectedChildId] = useState<string | null>(null);
  const [chatHistory, setChatHistory] = useState<LocalChatEntry[]>([]);
  const [input, setInput] = useState("");
  const [selectedProvider, setSelectedProvider] = useState<"MTN" | "AIRTEL">("MTN");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [paymentAmount, setPaymentAmount] = useState<number>(120000);
  const [paymentCurrency, setPaymentCurrency] = useState("UGX");
  const [paymentFeedback, setPaymentFeedback] = useState<string | null>(null);

  // Fetch parent dashboard data
  const { data: dashboard, refetch: refetchDashboard } = useQuery({
    queryKey: ["parent-dashboard", schoolId, parentId],
    queryFn: async () => {
      const res = await apiClient.get(`/parent/${schoolId}/parent/${parentId}/dashboard`);
      return res.data;
    },
    enabled: Boolean(schoolId && parentId) && navigator.onLine,
  });

  // Fetch notifications
  const { data: notificationsData, refetch: refetchNotifications } = useQuery({
    queryKey: ["parent-notifications", schoolId, parentId],
    queryFn: async () => {
      const res = await apiClient.get(`/parent/${schoolId}/parent/${parentId}/notifications`);
      return res.data;
    },
    enabled: Boolean(schoolId && parentId) && navigator.onLine,
  });

  const notifications: Notification[] = notificationsData?.notifications || [];
  const unreadCount = notifications.filter((n) => !n.is_read).length;

  // Fetch child details when selected
  const { data: childReport } = useQuery<ChildReport>({
    queryKey: ["child-details", schoolId, parentId, selectedChildId],
    queryFn: async () => {
      const res = await apiClient.get(
        `/parent/${schoolId}/parent/${parentId}/child/${selectedChildId}/details`
      );
      return res.data;
    },
    enabled: Boolean(selectedChildId) && navigator.onLine,
  });

  // Set first child as selected by default
  useEffect(() => {
    if (dashboard?.children && dashboard.children.length > 0 && !selectedChildId) {
      setSelectedChildId(dashboard.children[0].id);
    }
  }, [dashboard, selectedChildId]);

  // Payment mutation
  const paymentMutation = useMutation({
    mutationFn: async (payload: MobileMoneyPayload) => {
      const res = await apiClient.post(
        `/parent/${schoolId}/parent/${parentId}/pay-fees`,
        {
          student_id: selectedChildId,
          amount: payload.amount,
          provider: payload.provider.toLowerCase(),
          phone_number: payload.phone_number,
        }
      );
      return res.data;
    },
    onSuccess: (data) => {
      setPaymentFeedback(
        data.success
          ? `✅ Payment initiated! Check your ${selectedProvider} phone for prompt.`
          : `⚠️ ${data.message || "Payment queued for processing"}`
      );
      refetchDashboard();
    },
    onError: (error: any) => {
      setPaymentFeedback(
        `❌ ${error.response?.data?.detail || error.message || "Payment failed"}`
      );
    },
  });

  // Chat mutation
  const chatMutation = useMutation({
    mutationFn: async (message: string) => {
      const res = await apiClient.post(`/parent/${schoolId}/parent/${parentId}/chat/send`, {
        message,
        conversation_id: null,
      });
      return res.data;
    },
    onSuccess: (data) => {
      setChatHistory((prev) => [
        ...prev,
        {
          id: uuid(),
          role: "assistant",
          message: data.ai_response || "I'm here to help!",
          status: "sent",
        },
      ]);
    },
    onError: () => {
      setChatHistory((prev) => [
        ...prev,
        {
          id: uuid(),
          role: "assistant",
          message: "I'll answer when you're back online.",
          status: "pending",
        },
      ]);
    },
  });

  // Handle send message
  const handleSendMessage = () => {
    if (!input.trim()) return;

    const parentMessage: LocalChatEntry = {
      id: uuid(),
      role: "parent",
      message: input.trim(),
      status: navigator.onLine ? "sent" : "queued",
    };

    setChatHistory((prev) => [...prev, parentMessage]);
    setInput("");

    if (!navigator.onLine) {
      enqueueTask(
        `/parent/${schoolId}/parent/${parentId}/chat/send`,
        { message: input.trim() },
        "POST"
      );
      setChatHistory((prev) => [
        ...prev,
        {
          id: uuid(),
          role: "assistant",
          message: "I'll answer when you reconnect.",
          status: "queued",
        },
      ]);
      return;
    }

    chatMutation.mutate(input.trim());
  };

  // Handle payment
  const handlePayment = () => {
    if (!phoneNumber.trim()) {
      setPaymentFeedback("Please enter your mobile money phone number");
      return;
    }
    if (!selectedChildId) {
      setPaymentFeedback("Please select a child first");
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
      enqueueTask(`/parent/${schoolId}/parent/${parentId}/pay-fees`, payload, "POST");
      setPaymentFeedback("💾 Payment queued. Will process when you reconnect.");
      return;
    }

    paymentMutation.mutate(payload);
  };

  // Mark notification as read
  const markAsRead = async (notificationId: string) => {
    if (!navigator.onLine) return;

    try {
      await apiClient.post(
        `/parent/${schoolId}/parent/${parentId}/notifications/${notificationId}/read`
      );
      refetchNotifications();
    } catch (error) {
      console.error("Failed to mark as read:", error);
    }
  };

  const children: Child[] = dashboard?.children || [];
  const selectedChild = children.find((c) => c.id === selectedChildId);

  return (
    <section className="space-y-6 p-4">
      {/* Header */}
      <header className="space-y-2">
        <h1 className="text-3xl font-bold">Parent Portal</h1>
        <p className="text-slate-300">
          👨‍👩‍👧‍👦 View your children's attendance, grades, health, and fees. Pay via mobile money.
          Chat with AI. All in one app - no WhatsApp costs.
        </p>
      </header>

      {/* Child Selector */}
      {children.length > 0 && (
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
          <label className="text-sm font-medium mb-2 block">Select Child:</label>
          <div className="flex gap-2 flex-wrap">
            {children.map((child) => (
              <button
                key={child.id}
                onClick={() => setSelectedChildId(child.id)}
                className={`rounded-lg px-4 py-2 font-semibold ${selectedChildId === child.id
                    ? "bg-blue-600 text-white"
                    : "bg-slate-800 text-slate-300 hover:bg-slate-700"
                  }`}
              >
                {child.first_name} {child.last_name}
                <span className="ml-2 text-xs opacity-70">{child.class_name}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 border-b border-slate-700 overflow-x-auto">
        {["dashboard", "calendar", "notifications", "reports", "payments", "chat"].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab as any)}
            className={`px-4 py-2 font-semibold capitalize whitespace-nowrap ${activeTab === tab
                ? "border-b-2 border-blue-500 text-blue-500"
                : "text-slate-400 hover:text-slate-200"
              }`}
          >
            {tab}
            {tab === "notifications" && unreadCount > 0 && (
              <span className="ml-2 rounded-full bg-red-500 px-2 py-0.5 text-xs text-white">
                {unreadCount}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Dashboard Tab */}
      {activeTab === "dashboard" && (
        <div className="space-y-4">
          <BriefingWidget role="parent" />
          <div className="grid gap-4 md:grid-cols-3">
            {dashboard?.attendance_summary
              ?.filter((a: any) => a.student_id === selectedChildId)
              .map((summary: any) => (
                <div key={summary.student_id} className="rounded-2xl border border-emerald-500 bg-emerald-500/10 p-6">
                  <p className="text-sm text-emerald-100">Attendance Rate</p>
                  <p className="text-3xl font-bold mt-2">{summary.attendance_rate}%</p>
                  <p className="text-xs mt-1 text-emerald-200">
                    {summary.stats.present} present, {summary.stats.absent} absent
                  </p>
                </div>
              ))}

            {dashboard?.fee_summary
              ?.filter((f: any) => f.student_id === selectedChildId)
              .map((fee: any) => (
                <div key={fee.student_id} className="rounded-2xl border border-amber-500 bg-amber-500/10 p-6">
                  <p className="text-sm text-amber-100">Fee Balance</p>
                  <p className="text-3xl font-bold mt-2">
                    {paymentCurrency} {fee.total_balance.toLocaleString()}
                  </p>
                  <p className="text-xs mt-1 text-amber-200">
                    Paid: {fee.total_paid.toLocaleString()}
                  </p>
                </div>
              ))}

            <div className="rounded-2xl border border-blue-500 bg-blue-500/10 p-6">
              <p className="text-sm text-blue-100">Unread Notifications</p>
              <p className="text-3xl font-bold mt-2">{unreadCount}</p>
              <button
                onClick={() => setActiveTab("notifications")}
                className="text-xs mt-1 text-blue-200 hover:underline"
              >
                View all →
              </button>
            </div>
          </div>

          {selectedChild && (
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
              <h3 className="text-xl font-semibold mb-4">
                {selectedChild.first_name}'s Quick Stats
              </h3>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                  <p className="text-sm text-slate-400">Class</p>
                  <p className="text-lg font-semibold mt-1">{selectedChild.class_name}</p>
                </div>
                <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                  <p className="text-sm text-slate-400">Admission Number</p>
                  <p className="text-lg font-semibold mt-1">{selectedChild.admission_number}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Notifications Tab */}
      {activeTab === "notifications" && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">🔔 All Notifications</h2>

          {notifications.length === 0 ? (
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-8 text-center text-slate-400">
              No notifications yet. You'll receive alerts here for attendance, health, fees, and more.
            </div>
          ) : (
            <div className="space-y-3">
              {notifications.map((notif) => (
                <div
                  key={notif.id}
                  onClick={() => markAsRead(notif.id)}
                  className={`rounded-2xl border p-4 cursor-pointer transition ${notif.is_read
                      ? "border-slate-800 bg-slate-900/40"
                      : "border-blue-500 bg-blue-500/10 hover:bg-blue-500/20"
                    }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="text-xs uppercase font-semibold text-slate-400">
                          {notif.notification_type}
                        </span>
                        {!notif.is_read && (
                          <span className="rounded-full bg-red-500 px-2 py-0.5 text-xs font-semibold">
                            NEW
                          </span>
                        )}
                        {notif.priority === "high" && (
                          <span className="rounded-full bg-orange-500 px-2 py-0.5 text-xs font-semibold">
                            URGENT
                          </span>
                        )}
                      </div>
                      <h3 className="font-semibold mt-1">{notif.title}</h3>
                      <p className="mt-1 text-sm text-slate-300">{notif.message}</p>
                      <p className="mt-2 text-xs text-slate-400">
                        {dayjs(notif.created_at).fromNow()}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Reports Tab */}
      {activeTab === "reports" && selectedChild && (
        <div className="space-y-6">
          <h2 className="text-xl font-semibold">
            📊 Complete Report for {selectedChild.first_name}
          </h2>

          {/* Attendance Report */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
            <h3 className="text-lg font-semibold mb-4">📅 Attendance History (Last 30 Days)</h3>
            {childReport?.attendance && childReport.attendance.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-800 text-sm">
                  <thead>
                    <tr className="text-left text-xs uppercase text-slate-400">
                      <th className="px-3 py-2">Date</th>
                      <th className="px-3 py-2">Status</th>
                      <th className="px-3 py-2">Notes</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {childReport.attendance.map((record, idx) => (
                      <tr key={idx}>
                        <td className="px-3 py-2">{dayjs(record.date).format("MMM D, YYYY")}</td>
                        <td className="px-3 py-2">
                          <span
                            className={`rounded-full px-3 py-1 text-xs font-semibold ${record.status === "present"
                                ? "bg-green-500/20 text-green-100"
                                : record.status === "absent"
                                  ? "bg-red-500/20 text-red-100"
                                  : "bg-yellow-500/20 text-yellow-100"
                              }`}
                          >
                            {record.status}
                          </span>
                        </td>
                        <td className="px-3 py-2 text-slate-400">{record.notes || "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-slate-400">No attendance records available</p>
            )}
          </div>

          {/* Academic Results */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
            <h3 className="text-lg font-semibold mb-4">📚 Recent Academic Results</h3>
            {childReport?.recent_results && childReport.recent_results.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-800 text-sm">
                  <thead>
                    <tr className="text-left text-xs uppercase text-slate-400">
                      <th className="px-3 py-2">Date</th>
                      <th className="px-3 py-2">Assessment</th>
                      <th className="px-3 py-2">Subject</th>
                      <th className="px-3 py-2">Marks</th>
                      <th className="px-3 py-2">Grade</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {childReport.recent_results.map((result, idx) => (
                      <tr key={idx}>
                        <td className="px-3 py-2">{dayjs(result.date).format("MMM D")}</td>
                        <td className="px-3 py-2">{result.name}</td>
                        <td className="px-3 py-2">{result.subject}</td>
                        <td className="px-3 py-2">
                          {result.marks_obtained}/{result.max_marks}
                        </td>
                        <td className="px-3 py-2">
                          <span className="rounded-full bg-blue-500/20 px-3 py-1 text-xs font-semibold text-blue-100">
                            {result.grade}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-slate-400">No results available yet</p>
            )}
          </div>

          {/* Health Visits */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
            <h3 className="text-lg font-semibold mb-4">🏥 Health & Sickbay Visits</h3>
            {childReport?.health_visits && childReport.health_visits.length > 0 ? (
              <div className="space-y-3">
                {childReport.health_visits.map((visit, idx) => (
                  <div key={idx} className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="text-sm text-slate-400">
                          {dayjs(visit.visit_date).format("MMM D, YYYY - HH:mm")}
                        </p>
                        <p className="mt-2">
                          <span className="text-sm font-semibold">Symptoms:</span>{" "}
                          <span className="text-sm text-slate-300">{visit.symptoms}</span>
                        </p>
                        {visit.diagnosis && (
                          <p className="mt-1">
                            <span className="text-sm font-semibold">Diagnosis:</span>{" "}
                            <span className="text-sm text-slate-300">{visit.diagnosis}</span>
                          </p>
                        )}
                        {visit.treatment && (
                          <p className="mt-1">
                            <span className="text-sm font-semibold">Treatment:</span>{" "}
                            <span className="text-sm text-slate-300">{visit.treatment}</span>
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-slate-400">No health visits recorded</p>
            )}
          </div>

          {/* Fee Statement */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
            <h3 className="text-lg font-semibold mb-4">💰 Fee Statement</h3>
            {childReport?.fees && childReport.fees.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-800 text-sm">
                  <thead>
                    <tr className="text-left text-xs uppercase text-slate-400">
                      <th className="px-3 py-2">Fee Type</th>
                      <th className="px-3 py-2">Amount Due</th>
                      <th className="px-3 py-2">Paid</th>
                      <th className="px-3 py-2">Balance</th>
                      <th className="px-3 py-2">Due Date</th>
                      <th className="px-3 py-2">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {childReport.fees.map((fee, idx) => (
                      <tr key={idx}>
                        <td className="px-3 py-2">{fee.name}</td>
                        <td className="px-3 py-2">{fee.amount_due.toLocaleString()}</td>
                        <td className="px-3 py-2">{fee.amount_paid.toLocaleString()}</td>
                        <td className="px-3 py-2 font-semibold">
                          {fee.balance.toLocaleString()}
                        </td>
                        <td className="px-3 py-2">{dayjs(fee.due_date).format("MMM D, YYYY")}</td>
                        <td className="px-3 py-2">
                          <span
                            className={`rounded-full px-3 py-1 text-xs font-semibold ${fee.status === "paid"
                                ? "bg-green-500/20 text-green-100"
                                : fee.status === "overdue"
                                  ? "bg-red-500/20 text-red-100"
                                  : "bg-amber-500/20 text-amber-100"
                              }`}
                          >
                            {fee.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-slate-400">No fee records available</p>
            )}
          </div>
        </div>
      )}

      {/* Payments Tab */}
      {activeTab === "payments" && (
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
          <h2 className="text-xl font-semibold">💳 Pay School Fees via Mobile Money</h2>
          <p className="text-sm text-slate-300">
            Pay fees instantly using MTN Mobile Money or Airtel Money. Works offline - queues when disconnected.
          </p>

          <div className="grid gap-4 md:grid-cols-4">
            <div className="flex flex-col gap-2">
              <label className="text-xs uppercase tracking-wide text-slate-400">Provider</label>
              <select
                value={selectedProvider}
                onChange={(e) => setSelectedProvider(e.target.value as "MTN" | "AIRTEL")}
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
                onChange={(e) => setPaymentAmount(Number(e.target.value))}
                className="rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-xs uppercase tracking-wide text-slate-400">Currency</label>
              <input
                value={paymentCurrency}
                onChange={(e) => setPaymentCurrency(e.target.value.toUpperCase())}
                className="rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-xs uppercase tracking-wide text-slate-400">Phone Number</label>
              <input
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                placeholder="+256700000000"
                className="rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
              />
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={handlePayment}
              className="rounded-full bg-emerald-500 px-6 py-3 text-sm font-semibold text-black hover:bg-emerald-400"
              disabled={paymentMutation.isPending}
            >
              {paymentMutation.isPending
                ? "Processing..."
                : navigator.onLine
                  ? "Send Payment Request"
                  : "Queue Payment (Offline)"}
            </button>
            {paymentFeedback && (
              <span className="text-sm text-slate-300">{paymentFeedback}</span>
            )}
          </div>
        </div>
      )}

      {/* Chat Tab */}
      {activeTab === "chat" && flags?.enable_parent_chatbot && (
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
          <h2 className="text-xl font-semibold">💬 AI Assistant</h2>
          <p className="text-sm text-slate-300">
            Ask about fees, attendance, events, or request documents. No WhatsApp costs!
          </p>

          <div className="h-96 overflow-y-auto space-y-3 rounded-lg bg-slate-950/60 p-4">
            {chatHistory.length === 0 && (
              <p className="text-sm text-slate-400">
                Try: "What's my child's attendance rate this month?" or "Show me fee balance"
              </p>
            )}
            {chatHistory.map((entry) => (
              <div
                key={entry.id}
                className={`max-w-sm rounded-lg p-3 ${entry.role === "parent"
                    ? "ml-auto bg-blue-600 text-white"
                    : "bg-slate-800 text-slate-200"
                  }`}
              >
                <p>{entry.message}</p>
                {entry.status === "queued" && (
                  <p className="mt-1 text-[10px] uppercase tracking-wide opacity-70">
                    queued for sync
                  </p>
                )}
              </div>
            ))}
          </div>

          <div className="flex gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
              placeholder="Ask about fees, attendance, events..."
              className="flex-1 rounded-full border border-slate-700 bg-slate-950 px-4 py-2 text-sm"
            />
            <button
              onClick={handleSendMessage}
              className="rounded-full bg-blue-600 px-6 py-2 text-sm font-semibold hover:bg-blue-500"
            >
              {navigator.onLine ? "Send" : "Queue"}
            </button>
          </div>
        </div>
      )}

      {/* Calendar Tab */}
      {activeTab === "calendar" && <CalendarHub />}
    </section>
  );
};
