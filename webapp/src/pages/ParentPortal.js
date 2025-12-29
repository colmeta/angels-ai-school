import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * PRODUCTION Parent Portal - Complete PWA for Parents
 * - Real notifications with full access to child data
 * - All reports: attendance, grades, health, fees, incidents
 * - AI chatbot (no WhatsApp costs)
 * - Mobile money payments (MTN + Airtel)
 * - Offline-first with background sync
 * - Installable on any device
 */
import { useEffect, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { v4 as uuid } from "uuid";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
dayjs.extend(relativeTime);
import { useFeatureFlags } from "../hooks/useFeatureFlags";
import { useBrandingStore } from "../stores/branding";
import { useOfflineSync } from "../hooks/useOfflineSync";
import { apiClient } from "../lib/apiClient";
import BriefingWidget from "../components/Dashboard/BriefingWidget";
import CalendarHub from "./parent/CalendarHub";
export const ParentPortal = () => {
    const schoolId = useBrandingStore((state) => state.schoolId) || "demo-school";
    const parentId = localStorage.getItem("parent_id") || "demo-parent";
    const { data: flags } = useFeatureFlags(schoolId);
    const { tasks, enqueueTask } = useOfflineSync();
    const [activeTab, setActiveTab] = useState("dashboard");
    const [selectedChildId, setSelectedChildId] = useState(null);
    const [chatHistory, setChatHistory] = useState([]);
    const [input, setInput] = useState("");
    const [selectedProvider, setSelectedProvider] = useState("MTN");
    const [phoneNumber, setPhoneNumber] = useState("");
    const [paymentAmount, setPaymentAmount] = useState(120000);
    const [paymentCurrency, setPaymentCurrency] = useState("UGX");
    const [paymentFeedback, setPaymentFeedback] = useState(null);
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
    const notifications = notificationsData?.notifications || [];
    const unreadCount = notifications.filter((n) => !n.is_read).length;
    // Fetch child details when selected
    const { data: childReport } = useQuery({
        queryKey: ["child-details", schoolId, parentId, selectedChildId],
        queryFn: async () => {
            const res = await apiClient.get(`/parent/${schoolId}/parent/${parentId}/child/${selectedChildId}/details`);
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
        mutationFn: async (payload) => {
            const res = await apiClient.post(`/parent/${schoolId}/parent/${parentId}/pay-fees`, {
                student_id: selectedChildId,
                amount: payload.amount,
                provider: payload.provider.toLowerCase(),
                phone_number: payload.phone_number,
            });
            return res.data;
        },
        onSuccess: (data) => {
            setPaymentFeedback(data.success
                ? `✅ Payment initiated! Check your ${selectedProvider} phone for prompt.`
                : `⚠️ ${data.message || "Payment queued for processing"}`);
            refetchDashboard();
        },
        onError: (error) => {
            setPaymentFeedback(`❌ ${error.response?.data?.detail || error.message || "Payment failed"}`);
        },
    });
    // Chat mutation
    const chatMutation = useMutation({
        mutationFn: async (message) => {
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
        if (!input.trim())
            return;
        const parentMessage = {
            id: uuid(),
            role: "parent",
            message: input.trim(),
            status: navigator.onLine ? "sent" : "queued",
        };
        setChatHistory((prev) => [...prev, parentMessage]);
        setInput("");
        if (!navigator.onLine) {
            enqueueTask(`/parent/${schoolId}/parent/${parentId}/chat/send`, { message: input.trim() }, "POST");
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
        const payload = {
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
    const markAsRead = async (notificationId) => {
        if (!navigator.onLine)
            return;
        try {
            await apiClient.post(`/parent/${schoolId}/parent/${parentId}/notifications/${notificationId}/read`);
            refetchNotifications();
        }
        catch (error) {
            console.error("Failed to mark as read:", error);
        }
    };
    const children = dashboard?.children || [];
    const selectedChild = children.find((c) => c.id === selectedChildId);
    return (_jsxs("section", { className: "space-y-6 p-4", children: [_jsxs("header", { className: "space-y-2", children: [_jsx("h1", { className: "text-3xl font-bold", children: "Parent Portal" }), _jsx("p", { className: "text-slate-300", children: "\uD83D\uDC68\u200D\uD83D\uDC69\u200D\uD83D\uDC67\u200D\uD83D\uDC66 View your children's attendance, grades, health, and fees. Pay via mobile money. Chat with AI. All in one app - no WhatsApp costs." })] }), children.length > 0 && (_jsxs("div", { className: "rounded-2xl border border-slate-800 bg-slate-900/60 p-4", children: [_jsx("label", { className: "text-sm font-medium mb-2 block", children: "Select Child:" }), _jsx("div", { className: "flex gap-2 flex-wrap", children: children.map((child) => (_jsxs("button", { onClick: () => setSelectedChildId(child.id), className: `rounded-lg px-4 py-2 font-semibold ${selectedChildId === child.id
                                ? "bg-blue-600 text-white"
                                : "bg-slate-800 text-slate-300 hover:bg-slate-700"}`, children: [child.first_name, " ", child.last_name, _jsx("span", { className: "ml-2 text-xs opacity-70", children: child.class_name })] }, child.id))) })] })), _jsx("div", { className: "flex gap-2 border-b border-slate-700 overflow-x-auto", children: ["dashboard", "calendar", "notifications", "reports", "payments", "chat"].map((tab) => (_jsxs("button", { onClick: () => setActiveTab(tab), className: `px-4 py-2 font-semibold capitalize whitespace-nowrap ${activeTab === tab
                        ? "border-b-2 border-blue-500 text-blue-500"
                        : "text-slate-400 hover:text-slate-200"}`, children: [tab, tab === "notifications" && unreadCount > 0 && (_jsx("span", { className: "ml-2 rounded-full bg-red-500 px-2 py-0.5 text-xs text-white", children: unreadCount }))] }, tab))) }), activeTab === "dashboard" && (_jsxs("div", { className: "space-y-4", children: [_jsx(BriefingWidget, { role: "parent" }), _jsxs("div", { className: "grid gap-4 md:grid-cols-3", children: [dashboard?.attendance_summary
                                ?.filter((a) => a.student_id === selectedChildId)
                                .map((summary) => (_jsxs("div", { className: "rounded-2xl border border-emerald-500 bg-emerald-500/10 p-6", children: [_jsx("p", { className: "text-sm text-emerald-100", children: "Attendance Rate" }), _jsxs("p", { className: "text-3xl font-bold mt-2", children: [summary.attendance_rate, "%"] }), _jsxs("p", { className: "text-xs mt-1 text-emerald-200", children: [summary.stats.present, " present, ", summary.stats.absent, " absent"] })] }, summary.student_id))), dashboard?.fee_summary
                                ?.filter((f) => f.student_id === selectedChildId)
                                .map((fee) => (_jsxs("div", { className: "rounded-2xl border border-amber-500 bg-amber-500/10 p-6", children: [_jsx("p", { className: "text-sm text-amber-100", children: "Fee Balance" }), _jsxs("p", { className: "text-3xl font-bold mt-2", children: [paymentCurrency, " ", fee.total_balance.toLocaleString()] }), _jsxs("p", { className: "text-xs mt-1 text-amber-200", children: ["Paid: ", fee.total_paid.toLocaleString()] })] }, fee.student_id))), _jsxs("div", { className: "rounded-2xl border border-blue-500 bg-blue-500/10 p-6", children: [_jsx("p", { className: "text-sm text-blue-100", children: "Unread Notifications" }), _jsx("p", { className: "text-3xl font-bold mt-2", children: unreadCount }), _jsx("button", { onClick: () => setActiveTab("notifications"), className: "text-xs mt-1 text-blue-200 hover:underline", children: "View all \u2192" })] })] }), selectedChild && (_jsxs("div", { className: "rounded-2xl border border-slate-800 bg-slate-900/60 p-6", children: [_jsxs("h3", { className: "text-xl font-semibold mb-4", children: [selectedChild.first_name, "'s Quick Stats"] }), _jsxs("div", { className: "grid gap-4 md:grid-cols-2", children: [_jsxs("div", { className: "rounded-lg border border-slate-700 bg-slate-950 p-4", children: [_jsx("p", { className: "text-sm text-slate-400", children: "Class" }), _jsx("p", { className: "text-lg font-semibold mt-1", children: selectedChild.class_name })] }), _jsxs("div", { className: "rounded-lg border border-slate-700 bg-slate-950 p-4", children: [_jsx("p", { className: "text-sm text-slate-400", children: "Admission Number" }), _jsx("p", { className: "text-lg font-semibold mt-1", children: selectedChild.admission_number })] })] })] }))] })), activeTab === "notifications" && (_jsxs("div", { className: "space-y-4", children: [_jsx("h2", { className: "text-xl font-semibold", children: "\uD83D\uDD14 All Notifications" }), notifications.length === 0 ? (_jsx("div", { className: "rounded-2xl border border-slate-800 bg-slate-900/60 p-8 text-center text-slate-400", children: "No notifications yet. You'll receive alerts here for attendance, health, fees, and more." })) : (_jsx("div", { className: "space-y-3", children: notifications.map((notif) => (_jsx("div", { onClick: () => markAsRead(notif.id), className: `rounded-2xl border p-4 cursor-pointer transition ${notif.is_read
                                ? "border-slate-800 bg-slate-900/40"
                                : "border-blue-500 bg-blue-500/10 hover:bg-blue-500/20"}`, children: _jsx("div", { className: "flex items-start justify-between", children: _jsxs("div", { className: "flex-1", children: [_jsxs("div", { className: "flex items-center gap-2", children: [_jsx("span", { className: "text-xs uppercase font-semibold text-slate-400", children: notif.notification_type }), !notif.is_read && (_jsx("span", { className: "rounded-full bg-red-500 px-2 py-0.5 text-xs font-semibold", children: "NEW" })), notif.priority === "high" && (_jsx("span", { className: "rounded-full bg-orange-500 px-2 py-0.5 text-xs font-semibold", children: "URGENT" }))] }), _jsx("h3", { className: "font-semibold mt-1", children: notif.title }), _jsx("p", { className: "mt-1 text-sm text-slate-300", children: notif.message }), _jsx("p", { className: "mt-2 text-xs text-slate-400", children: dayjs(notif.created_at).fromNow() })] }) }) }, notif.id))) }))] })), activeTab === "reports" && selectedChild && (_jsxs("div", { className: "space-y-6", children: [_jsxs("h2", { className: "text-xl font-semibold", children: ["\uD83D\uDCCA Complete Report for ", selectedChild.first_name] }), _jsxs("div", { className: "rounded-2xl border border-slate-800 bg-slate-900/60 p-6", children: [_jsx("h3", { className: "text-lg font-semibold mb-4", children: "\uD83D\uDCC5 Attendance History (Last 30 Days)" }), childReport?.attendance && childReport.attendance.length > 0 ? (_jsx("div", { className: "overflow-x-auto", children: _jsxs("table", { className: "min-w-full divide-y divide-slate-800 text-sm", children: [_jsx("thead", { children: _jsxs("tr", { className: "text-left text-xs uppercase text-slate-400", children: [_jsx("th", { className: "px-3 py-2", children: "Date" }), _jsx("th", { className: "px-3 py-2", children: "Status" }), _jsx("th", { className: "px-3 py-2", children: "Notes" })] }) }), _jsx("tbody", { className: "divide-y divide-slate-800", children: childReport.attendance.map((record, idx) => (_jsxs("tr", { children: [_jsx("td", { className: "px-3 py-2", children: dayjs(record.date).format("MMM D, YYYY") }), _jsx("td", { className: "px-3 py-2", children: _jsx("span", { className: `rounded-full px-3 py-1 text-xs font-semibold ${record.status === "present"
                                                                ? "bg-green-500/20 text-green-100"
                                                                : record.status === "absent"
                                                                    ? "bg-red-500/20 text-red-100"
                                                                    : "bg-yellow-500/20 text-yellow-100"}`, children: record.status }) }), _jsx("td", { className: "px-3 py-2 text-slate-400", children: record.notes || "—" })] }, idx))) })] }) })) : (_jsx("p", { className: "text-slate-400", children: "No attendance records available" }))] }), _jsxs("div", { className: "rounded-2xl border border-slate-800 bg-slate-900/60 p-6", children: [_jsx("h3", { className: "text-lg font-semibold mb-4", children: "\uD83D\uDCDA Recent Academic Results" }), childReport?.recent_results && childReport.recent_results.length > 0 ? (_jsx("div", { className: "overflow-x-auto", children: _jsxs("table", { className: "min-w-full divide-y divide-slate-800 text-sm", children: [_jsx("thead", { children: _jsxs("tr", { className: "text-left text-xs uppercase text-slate-400", children: [_jsx("th", { className: "px-3 py-2", children: "Date" }), _jsx("th", { className: "px-3 py-2", children: "Assessment" }), _jsx("th", { className: "px-3 py-2", children: "Subject" }), _jsx("th", { className: "px-3 py-2", children: "Marks" }), _jsx("th", { className: "px-3 py-2", children: "Grade" })] }) }), _jsx("tbody", { className: "divide-y divide-slate-800", children: childReport.recent_results.map((result, idx) => (_jsxs("tr", { children: [_jsx("td", { className: "px-3 py-2", children: dayjs(result.date).format("MMM D") }), _jsx("td", { className: "px-3 py-2", children: result.name }), _jsx("td", { className: "px-3 py-2", children: result.subject }), _jsxs("td", { className: "px-3 py-2", children: [result.marks_obtained, "/", result.max_marks] }), _jsx("td", { className: "px-3 py-2", children: _jsx("span", { className: "rounded-full bg-blue-500/20 px-3 py-1 text-xs font-semibold text-blue-100", children: result.grade }) })] }, idx))) })] }) })) : (_jsx("p", { className: "text-slate-400", children: "No results available yet" }))] }), _jsxs("div", { className: "rounded-2xl border border-slate-800 bg-slate-900/60 p-6", children: [_jsx("h3", { className: "text-lg font-semibold mb-4", children: "\uD83C\uDFE5 Health & Sickbay Visits" }), childReport?.health_visits && childReport.health_visits.length > 0 ? (_jsx("div", { className: "space-y-3", children: childReport.health_visits.map((visit, idx) => (_jsx("div", { className: "rounded-lg border border-slate-700 bg-slate-950 p-4", children: _jsx("div", { className: "flex justify-between items-start", children: _jsxs("div", { children: [_jsx("p", { className: "text-sm text-slate-400", children: dayjs(visit.visit_date).format("MMM D, YYYY - HH:mm") }), _jsxs("p", { className: "mt-2", children: [_jsx("span", { className: "text-sm font-semibold", children: "Symptoms:" }), " ", _jsx("span", { className: "text-sm text-slate-300", children: visit.symptoms })] }), visit.diagnosis && (_jsxs("p", { className: "mt-1", children: [_jsx("span", { className: "text-sm font-semibold", children: "Diagnosis:" }), " ", _jsx("span", { className: "text-sm text-slate-300", children: visit.diagnosis })] })), visit.treatment && (_jsxs("p", { className: "mt-1", children: [_jsx("span", { className: "text-sm font-semibold", children: "Treatment:" }), " ", _jsx("span", { className: "text-sm text-slate-300", children: visit.treatment })] }))] }) }) }, idx))) })) : (_jsx("p", { className: "text-slate-400", children: "No health visits recorded" }))] }), _jsxs("div", { className: "rounded-2xl border border-slate-800 bg-slate-900/60 p-6", children: [_jsx("h3", { className: "text-lg font-semibold mb-4", children: "\uD83D\uDCB0 Fee Statement" }), childReport?.fees && childReport.fees.length > 0 ? (_jsx("div", { className: "overflow-x-auto", children: _jsxs("table", { className: "min-w-full divide-y divide-slate-800 text-sm", children: [_jsx("thead", { children: _jsxs("tr", { className: "text-left text-xs uppercase text-slate-400", children: [_jsx("th", { className: "px-3 py-2", children: "Fee Type" }), _jsx("th", { className: "px-3 py-2", children: "Amount Due" }), _jsx("th", { className: "px-3 py-2", children: "Paid" }), _jsx("th", { className: "px-3 py-2", children: "Balance" }), _jsx("th", { className: "px-3 py-2", children: "Due Date" }), _jsx("th", { className: "px-3 py-2", children: "Status" })] }) }), _jsx("tbody", { className: "divide-y divide-slate-800", children: childReport.fees.map((fee, idx) => (_jsxs("tr", { children: [_jsx("td", { className: "px-3 py-2", children: fee.name }), _jsx("td", { className: "px-3 py-2", children: fee.amount_due.toLocaleString() }), _jsx("td", { className: "px-3 py-2", children: fee.amount_paid.toLocaleString() }), _jsx("td", { className: "px-3 py-2 font-semibold", children: fee.balance.toLocaleString() }), _jsx("td", { className: "px-3 py-2", children: dayjs(fee.due_date).format("MMM D, YYYY") }), _jsx("td", { className: "px-3 py-2", children: _jsx("span", { className: `rounded-full px-3 py-1 text-xs font-semibold ${fee.status === "paid"
                                                                ? "bg-green-500/20 text-green-100"
                                                                : fee.status === "overdue"
                                                                    ? "bg-red-500/20 text-red-100"
                                                                    : "bg-amber-500/20 text-amber-100"}`, children: fee.status }) })] }, idx))) })] }) })) : (_jsx("p", { className: "text-slate-400", children: "No fee records available" }))] })] })), activeTab === "payments" && (_jsxs("div", { className: "rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4", children: [_jsx("h2", { className: "text-xl font-semibold", children: "\uD83D\uDCB3 Pay School Fees via Mobile Money" }), _jsx("p", { className: "text-sm text-slate-300", children: "Pay fees instantly using MTN Mobile Money or Airtel Money. Works offline - queues when disconnected." }), _jsxs("div", { className: "grid gap-4 md:grid-cols-4", children: [_jsxs("div", { className: "flex flex-col gap-2", children: [_jsx("label", { className: "text-xs uppercase tracking-wide text-slate-400", children: "Provider" }), _jsxs("select", { value: selectedProvider, onChange: (e) => setSelectedProvider(e.target.value), className: "rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm", children: [_jsx("option", { value: "MTN", children: "MTN Mobile Money" }), _jsx("option", { value: "AIRTEL", children: "Airtel Money" })] })] }), _jsxs("div", { className: "flex flex-col gap-2", children: [_jsx("label", { className: "text-xs uppercase tracking-wide text-slate-400", children: "Amount" }), _jsx("input", { type: "number", min: 1000, value: paymentAmount, onChange: (e) => setPaymentAmount(Number(e.target.value)), className: "rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm" })] }), _jsxs("div", { className: "flex flex-col gap-2", children: [_jsx("label", { className: "text-xs uppercase tracking-wide text-slate-400", children: "Currency" }), _jsx("input", { value: paymentCurrency, onChange: (e) => setPaymentCurrency(e.target.value.toUpperCase()), className: "rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm" })] }), _jsxs("div", { className: "flex flex-col gap-2", children: [_jsx("label", { className: "text-xs uppercase tracking-wide text-slate-400", children: "Phone Number" }), _jsx("input", { value: phoneNumber, onChange: (e) => setPhoneNumber(e.target.value), placeholder: "+256700000000", className: "rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm" })] })] }), _jsxs("div", { className: "flex flex-wrap items-center gap-3", children: [_jsx("button", { onClick: handlePayment, className: "rounded-full bg-emerald-500 px-6 py-3 text-sm font-semibold text-black hover:bg-emerald-400", disabled: paymentMutation.isPending, children: paymentMutation.isPending
                                    ? "Processing..."
                                    : navigator.onLine
                                        ? "Send Payment Request"
                                        : "Queue Payment (Offline)" }), paymentFeedback && (_jsx("span", { className: "text-sm text-slate-300", children: paymentFeedback }))] })] })), activeTab === "chat" && flags?.enable_parent_chatbot && (_jsxs("div", { className: "rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4", children: [_jsx("h2", { className: "text-xl font-semibold", children: "\uD83D\uDCAC AI Assistant" }), _jsx("p", { className: "text-sm text-slate-300", children: "Ask about fees, attendance, events, or request documents. No WhatsApp costs!" }), _jsxs("div", { className: "h-96 overflow-y-auto space-y-3 rounded-lg bg-slate-950/60 p-4", children: [chatHistory.length === 0 && (_jsx("p", { className: "text-sm text-slate-400", children: "Try: \"What's my child's attendance rate this month?\" or \"Show me fee balance\"" })), chatHistory.map((entry) => (_jsxs("div", { className: `max-w-sm rounded-lg p-3 ${entry.role === "parent"
                                    ? "ml-auto bg-blue-600 text-white"
                                    : "bg-slate-800 text-slate-200"}`, children: [_jsx("p", { children: entry.message }), entry.status === "queued" && (_jsx("p", { className: "mt-1 text-[10px] uppercase tracking-wide opacity-70", children: "queued for sync" }))] }, entry.id)))] }), _jsxs("div", { className: "flex gap-2", children: [_jsx("input", { value: input, onChange: (e) => setInput(e.target.value), onKeyPress: (e) => e.key === "Enter" && handleSendMessage(), placeholder: "Ask about fees, attendance, events...", className: "flex-1 rounded-full border border-slate-700 bg-slate-950 px-4 py-2 text-sm" }), _jsx("button", { onClick: handleSendMessage, className: "rounded-full bg-blue-600 px-6 py-2 text-sm font-semibold hover:bg-blue-500", children: navigator.onLine ? "Send" : "Queue" })] })] })), activeTab === "calendar" && _jsx(CalendarHub, {})] }));
};
