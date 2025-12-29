/**
 * Director Dashboard (Part of the "Director OS")
 * ============================================
 * High-level strategic overview for School Directors/Owners.
 * Consumes the "Digital CEO" agent API (api/routes/director.py).
 * Prioritizes high-level financial & academic health metrics.
 */

import { useQuery } from "@tanstack/react-query";
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    AreaChart, Area
} from "recharts";
import {
    TrendingUp, TrendingDown, Users, DollarSign,
    AlertTriangle, Activity, Layout, Upload, ShieldCheck, Brain, CreditCard
} from "lucide-react";
import { motion } from "framer-motion";
import clsx from "clsx";

import { apiClient } from "../../lib/apiClient";
import { useBrandingStore } from "../../stores/branding";

// --- Types ---

interface DirectorOverview {
    health_score: number;
    finance: {
        status: "healthy" | "warning" | "distressed" | "unknown";
        collection_rate: number;
        monthly_revenue: number;
    };
    academics: {
        status: "healthy" | "warning" | "critical";
        average_grade: string;
        attendance_rate: number;
    };
    strategic_insight?: string;
    alerts: string[];
}

interface KPICardProps {
    title: string;
    value: string | number;
    trend?: number;
    status: 'good' | 'warning' | 'alert';
    icon: React.ElementType;
    subtext?: string;
}

const KPICard = ({ title, value, status, icon: Icon, subtext }: KPICardProps) => (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 hover:border-slate-700 transition-colors">
        <div className="flex justify-between items-start mb-4">
            <div>
                <p className="text-slate-400 text-sm font-medium uppercase tracking-wide">{title}</p>
                <h3 className="text-3xl font-bold text-white mt-2">{value}</h3>
            </div>
            <div className={clsx(
                "p-3 rounded-xl",
                status === 'good' ? "bg-emerald-500/10 text-emerald-500" :
                    status === 'warning' ? "bg-amber-500/10 text-amber-500" :
                        "bg-red-500/10 text-red-500"
            )}>
                <Icon size={24} />
            </div>
        </div>
        {subtext && (
            <div className="flex items-center gap-2">
                <span className={clsx(
                    "text-sm font-medium",
                    status === 'good' ? "text-emerald-500" :
                        status === 'warning' ? "text-amber-500" : "text-red-500"
                )}>
                    {subtext}
                </span>
            </div>
        )}
    </div>
);

export const DirectorDashboard = () => {
    const schoolId = useBrandingStore((state) => state.schoolId) || "demo-school";

    // 1. Fetch One-Minute Overview (Digital CEO Logic)
    const { data: overviewData, isLoading: isLoadingOverview } = useQuery<DirectorOverview>({
        queryKey: ["director-overview", schoolId],
        queryFn: async () => {
            const res = await apiClient.get(`/${schoolId}/director/overview`);
            return res.data.data;
        },
        enabled: Boolean(schoolId),
    });

    // 2. Fetch Trends for Charts
    const { data: trendsData } = useQuery({
        queryKey: ["director-trends", schoolId],
        queryFn: async () => {
            const res = await apiClient.get(`/${schoolId}/director/trends`);
            return res.data.trends || [];
        },
        enabled: Boolean(schoolId),
    });

    const isHealthy = overviewData?.health_score && overviewData.health_score > 80;

    return (
        <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-8 pb-20">
            {/* AI Strategic Commentary */}
            {overviewData?.strategic_insight && (
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-indigo-600/10 border border-indigo-500/30 rounded-2xl p-6 flex gap-4 items-center shadow-lg shadow-indigo-500/5"
                >
                    <div className="bg-indigo-600 p-3 rounded-xl shadow-lg shadow-indigo-500/20">
                        <Brain size={24} className="text-white" />
                    </div>
                    <div>
                        <h3 className="text-indigo-300 text-xs font-bold uppercase tracking-widest mb-1 flex items-center gap-2">
                            Digital CEO Perspective
                            <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse" />
                        </h3>
                        <p className="text-white font-medium italic leading-relaxed">
                            "{overviewData.strategic_insight}"
                        </p>
                    </div>
                </motion.div>
            )}

            {/* Header */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-white">Director's Suite</h1>
                    <p className="text-slate-400 mt-1">Strategic oversight for {schoolId.replace(/-/g, ' ')}</p>
                </div>
                <div className="flex items-center gap-3">
                    <div className={clsx(
                        "px-4 py-1.5 rounded-full text-sm font-medium border flex items-center gap-2",
                        isHealthy
                            ? "bg-emerald-500/10 text-emerald-500 border-emerald-500/20"
                            : "bg-amber-500/10 text-amber-500 border-amber-500/20"
                    )}>
                        <ShieldCheck size={16} />
                        {isHealthy ? "System Healthy" : "Attention Needed"}
                    </div>
                </div>
            </div>

            {/* Quick Actions (Strategic Tools) */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <button
                    onClick={() => window.location.href = '/tools/template-builder'}
                    className="bg-indigo-600/10 hover:bg-indigo-600/20 border border-indigo-500/30 text-indigo-300 p-4 rounded-2xl flex flex-col items-center justify-center gap-2 transition-all"
                >
                    <Layout size={24} className="mb-1" />
                    <span className="text-sm font-semibold">Report Builder</span>
                </button>
                <button
                    onClick={() => window.location.href = '/tools/import'}
                    className="bg-emerald-600/10 hover:bg-emerald-600/20 border border-emerald-500/30 text-emerald-300 p-4 rounded-2xl flex flex-col items-center justify-center gap-2 transition-all"
                >
                    <Upload size={24} className="mb-1" />
                    <span className="text-sm font-semibold">Universal Import</span>
                </button>
                <button
                    onClick={() => window.location.href = '/tools/document-hub'}
                    className="bg-blue-600/10 hover:bg-blue-600/20 border border-blue-500/30 text-blue-300 p-4 rounded-2xl flex flex-col items-center justify-center gap-2 transition-all"
                >
                    <CreditCard size={24} className="mb-1" />
                    <span className="text-sm font-semibold">Document Hub</span>
                </button>
                <button
                    className="bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 p-4 rounded-2xl flex flex-col items-center justify-center gap-2 transition-all"
                >
                    <Activity size={24} className="mb-1" />
                    <span className="text-sm font-semibold">Audit Logs</span>
                </button>
            </div>

            {/* KPI Grid - Real Data */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <KPICard
                    title="Fee Collection"
                    value={`${overviewData?.finance?.collection_rate || 0}%`}
                    status={
                        (overviewData?.finance?.collection_rate || 0) > 80 ? 'good' :
                            (overviewData?.finance?.collection_rate || 0) > 50 ? 'warning' : 'alert'
                    }
                    icon={DollarSign}
                    subtext={isLoadingOverview ? "Calculating..." : "Target: 90%"}
                />
                <KPICard
                    title="Attendance"
                    value={`${overviewData?.academics?.attendance_rate || 0}%`}
                    status={
                        (overviewData?.academics?.attendance_rate || 0) > 90 ? 'good' : 'warning'
                    }
                    icon={Users}
                    subtext="Daily Average"
                />
                <KPICard
                    title="Academic Health"
                    value={overviewData?.academics?.average_grade || "-"}
                    status={overviewData?.academics?.status === "healthy" ? "good" : "warning"}
                    icon={Activity}
                    subtext="School Wide GPA"
                />
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                {/* Financial Trajectory */}
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                    <h3 className="text-lg font-semibold text-white mb-6">Revenue Trajectory (6 Months)</h3>
                    <div className="h-[300px] w-full">
                        {trendsData?.length > 0 ? (
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={trendsData}>
                                    <defs>
                                        <linearGradient id="colorFees" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#10B981" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                                    <XAxis dataKey="name" stroke="#64748b" axisLine={false} tickLine={false} />
                                    <YAxis stroke="#64748b" axisLine={false} tickLine={false} />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px' }}
                                    />
                                    <Area
                                        type="monotone"
                                        dataKey="fees"
                                        stroke="#10B981"
                                        strokeWidth={3}
                                        fillOpacity={1}
                                        fill="url(#colorFees)"
                                    />
                                </AreaChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="h-full flex items-center justify-center text-slate-500">
                                Not enough data for trends yet.
                            </div>
                        )}
                    </div>
                </div>

                {/* Attendance vs Performance */}
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                    <h3 className="text-lg font-semibold text-white mb-6">Attendance Overview</h3>
                    <div className="h-[300px] w-full">
                        {trendsData?.length > 0 ? (
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={trendsData}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                                    <XAxis dataKey="name" stroke="#64748b" axisLine={false} tickLine={false} />
                                    <YAxis stroke="#64748b" axisLine={false} tickLine={false} />
                                    <Tooltip
                                        cursor={{ fill: '#1e293b' }}
                                        contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px' }}
                                    />
                                    <Bar dataKey="attendance" fill="#3B82F6" radius={[4, 4, 0, 0]} barSize={40} />
                                </BarChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="h-full flex items-center justify-center text-slate-500">
                                Waiting for attendance data...
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Critical Alerts - The "Red Light" Zone */}
            {(!overviewData?.finance?.status || overviewData.finance.status === "distressed") && (
                <div className="bg-red-500/5 border border-red-500/20 rounded-2xl p-6 animate-in fade-in slide-in-from-bottom-5">
                    <h3 className="text-lg font-semibold text-red-500 flex items-center gap-2 mb-4">
                        <AlertTriangle size={20} />
                        Critical Attention Needed
                    </h3>
                    <div className="space-y-4">
                        <div className="flex items-start gap-4 p-4 bg-red-500/10 rounded-xl border border-red-500/10">
                            <div className="w-2 h-2 mt-2 rounded-full bg-red-500" />
                            <div>
                                <h4 className="text-white font-medium">Financial Health Check</h4>
                                <p className="text-slate-400 text-sm mt-1">
                                    Fee collection is below target ({overviewData?.finance?.collection_rate || 0}%).
                                    Consider running a bulk SMS reminder campaign via the Admin Dashboard.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};