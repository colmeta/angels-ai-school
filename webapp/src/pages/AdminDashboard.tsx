import { useQuery } from "@tanstack/react-query";

import { clarityClient } from "../lib/apiClient";
import { useBrandingStore } from "../stores/branding";
import BriefingWidget from "../components/Dashboard/BriefingWidget";

interface ClaritySummary {
  success: boolean;
  analysis?: {
    summary: string;
    findings: string[];
    next_steps: string;
  };
  status?: string;
}

export const AdminDashboard = () => {
  const { schoolId, displayName } = useBrandingStore();

  const { data, isFetching, refetch } = useQuery({
    queryKey: ["executive-briefing", schoolId],
    queryFn: async () => {
      const { data: response } = await clarityClient.post<ClaritySummary>("/analyze", {
        directive: `Provide today’s executive briefing for ${displayName} in Uganda, summarizing finances, academics, parent sentiment, and safety.`,
        domain: "education",
      });
      return response;
    },
    refetchInterval: 1000 * 60 * 60,
  });

  return (
    <section className="space-y-6">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Executive Command Center</h1>
          <p className="text-slate-300">
            Daily strategic intelligence, powered by the Angels AI Digital CEO + Clarity engine.
          </p>
        </div>
        <button
          className="rounded-full bg-blue-600 px-4 py-2 text-sm font-semibold hover:bg-blue-500"
          onClick={() => refetch()}
        >
          Refresh Briefing
        </button>
      </header>

      <BriefingWidget role="admin" />

      <div className="grid gap-4 md:grid-cols-3">
        <MetricCard label="Fee Collection Rate" value="92%" trend="+4% vs last term" />
        <MetricCard label="Attendance Health" value="96%" trend="On target" />
        <MetricCard label="Parent Satisfaction" value="4.7 / 5" trend="+0.3 this week" />
      </div>

      <div className="rounded-3xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">In-Depth Strategy Intelligence</h2>
          {isFetching && <span className="text-xs text-blue-300 animate-pulse">Refreshing…</span>}
        </div>
        <p className="text-sm text-slate-300 leading-relaxed">
          {data?.analysis?.summary ??
            "Deeper strategic analysis will appear here. The Executive Assistant above handles your immediate daily briefings."}
        </p>
        <div className="grid gap-3 md:grid-cols-2">
          <ListCard title="Key Findings" items={data?.analysis?.findings ?? placeholderFindings} />
          <ListCard title="Next Steps" items={[data?.analysis?.next_steps ?? fallbackNextSteps]} />
        </div>
      </div>
    </section>
  );
};

interface MetricCardProps {
  label: string;
  value: string;
  trend: string;
}

const MetricCard = ({ label, value, trend }: MetricCardProps) => (
  <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
    <p className="text-xs uppercase tracking-wide text-slate-400">{label}</p>
    <p className="text-2xl font-semibold mt-2">{value}</p>
    <p className="text-xs text-emerald-400 mt-1">{trend}</p>
  </div>
);

const placeholderFindings = [
  "Offline tasks syncing queue is healthy.",
  "Parent chatbot deflected 85% of inquiries without human escalation.",
  "Security checks completed for all visitors today.",
];

const fallbackNextSteps =
  "Once reconnected, dispatch comprehensive report to leadership and fetch new directives.";

interface ListCardProps {
  title: string;
  items: string[];
}

const ListCard = ({ title, items }: ListCardProps) => (
  <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4">
    <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-400 mb-2">
      {title}
    </h3>
    <ul className="space-y-2 text-sm text-slate-300">
      {items.map((item, index) => (
        <li key={`${title}-${index}`} className="flex gap-2">
          <span className="mt-1 h-1.5 w-1.5 rounded-full bg-slate-500" />
          <span>{item}</span>
        </li>
      ))}
    </ul>
  </div>
);
