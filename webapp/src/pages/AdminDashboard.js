import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useQuery } from "@tanstack/react-query";
import { clarityClient } from "../lib/apiClient";
import { useBrandingStore } from "../stores/branding";
import BriefingWidget from "../components/Dashboard/BriefingWidget";
export const AdminDashboard = () => {
    const { schoolId, displayName } = useBrandingStore();
    const { data, isFetching, refetch } = useQuery({
        queryKey: ["executive-briefing", schoolId],
        queryFn: async () => {
            const { data: response } = await clarityClient.post("/analyze", {
                directive: `Provide today’s executive briefing for ${displayName} in Uganda, summarizing finances, academics, parent sentiment, and safety.`,
                domain: "education",
            });
            return response;
        },
        refetchInterval: 1000 * 60 * 60,
    });
    return (_jsxs("section", { className: "space-y-6", children: [_jsxs("header", { className: "flex items-center justify-between", children: [_jsxs("div", { children: [_jsx("h1", { className: "text-2xl font-semibold", children: "Executive Command Center" }), _jsx("p", { className: "text-slate-300", children: "Daily strategic intelligence, powered by the Angels AI Digital CEO + Clarity engine." })] }), _jsx("button", { className: "rounded-full bg-blue-600 px-4 py-2 text-sm font-semibold hover:bg-blue-500", onClick: () => refetch(), children: "Refresh Briefing" })] }), _jsx(BriefingWidget, { role: "admin" }), _jsxs("div", { className: "grid gap-4 md:grid-cols-3", children: [_jsx(MetricCard, { label: "Fee Collection Rate", value: "92%", trend: "+4% vs last term" }), _jsx(MetricCard, { label: "Attendance Health", value: "96%", trend: "On target" }), _jsx(MetricCard, { label: "Parent Satisfaction", value: "4.7 / 5", trend: "+0.3 this week" })] }), _jsxs("div", { className: "rounded-3xl border border-slate-800 bg-slate-900/60 p-6 space-y-4", children: [_jsxs("div", { className: "flex items-center justify-between", children: [_jsx("h2", { className: "text-xl font-semibold", children: "In-Depth Strategy Intelligence" }), isFetching && _jsx("span", { className: "text-xs text-blue-300 animate-pulse", children: "Refreshing\u2026" })] }), _jsx("p", { className: "text-sm text-slate-300 leading-relaxed", children: data?.analysis?.summary ??
                            "Deeper strategic analysis will appear here. The Executive Assistant above handles your immediate daily briefings." }), _jsxs("div", { className: "grid gap-3 md:grid-cols-2", children: [_jsx(ListCard, { title: "Key Findings", items: data?.analysis?.findings ?? placeholderFindings }), _jsx(ListCard, { title: "Next Steps", items: [data?.analysis?.next_steps ?? fallbackNextSteps] })] })] })] }));
};
const MetricCard = ({ label, value, trend }) => (_jsxs("div", { className: "rounded-2xl border border-slate-800 bg-slate-900/70 p-5", children: [_jsx("p", { className: "text-xs uppercase tracking-wide text-slate-400", children: label }), _jsx("p", { className: "text-2xl font-semibold mt-2", children: value }), _jsx("p", { className: "text-xs text-emerald-400 mt-1", children: trend })] }));
const placeholderFindings = [
    "Offline tasks syncing queue is healthy.",
    "Parent chatbot deflected 85% of inquiries without human escalation.",
    "Security checks completed for all visitors today.",
];
const fallbackNextSteps = "Once reconnected, dispatch comprehensive report to leadership and fetch new directives.";
const ListCard = ({ title, items }) => (_jsxs("div", { className: "rounded-2xl border border-slate-800 bg-slate-900/70 p-4", children: [_jsx("h3", { className: "text-sm font-semibold uppercase tracking-wide text-slate-400 mb-2", children: title }), _jsx("ul", { className: "space-y-2 text-sm text-slate-300", children: items.map((item, index) => (_jsxs("li", { className: "flex gap-2", children: [_jsx("span", { className: "mt-1 h-1.5 w-1.5 rounded-full bg-slate-500" }), _jsx("span", { children: item })] }, `${title}-${index}`))) })] }));
