import { useState, useEffect } from "react";
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    AreaChart, Area
} from "recharts";
import {
    TrendingUp, TrendingDown, Users, DollarSign,
    AlertTriangle, CheckCircle, Activity
} from "lucide-react";
import clsx from "clsx";

// Mock Data for "Immediate Visualization" before backend hookup
const MOCK_TREND_DATA = [
    { name: 'Jan', fees: 4000, attendance: 2400 },
    { name: 'Feb', fees: 3000, attendance: 1398 },
    { name: 'Mar', fees: 2000, attendance: 9800 },
    { name: 'Apr', fees: 2780, attendance: 3908 },
    { name: 'May', fees: 1890, attendance: 4800 },
    { name: 'Jun', fees: 2390, attendance: 3800 },
    { name: 'Jul', fees: 3490, attendance: 4300 },
];

const KPICard = ({ title, value, trend, status, icon: Icon }: any) => (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
        <div className="flex justify-between items-start mb-4">
            <div>
                <p className="text-slate-400 text-sm font-medium">{title}</p>
                <h3 className="text-3xl font-bold text-white mt-1">{value}</h3>
            </div>
            <div className={clsx(
                "p-2 rounded-lg",
                status === 'good' ? "bg-green-500/10 text-green-500" :
                    status === 'warning' ? "bg-yellow-500/10 text-yellow-500" :
                        "bg-red-500/10 text-red-500"
            )}>
                <Icon size={24} />
            </div>
        </div>
        <div className="flex items-center gap-2">
            {trend > 0 ? (
                <TrendingUp size={16} className="text-green-500" />
            ) : (
                <TrendingDown size={16} className="text-red-500" />
            )}
            <span className={clsx(
                "text-sm font-medium",
                trend > 0 ? "text-green-500" : "text-red-500"
            )}>
                {Math.abs(trend)}% vs last month
            </span>
        </div>
    </div>
);

export const DirectorDashboard = () => {
    // In future: useDigitalCEO hook here to fetch real data

    return (
        <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-8">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-white">School Pulse</h1>
                    <p className="text-slate-400">One-minute overview for the Director</p>
                </div>
                <div className="flex gap-2">
                    <span className="px-3 py-1 bg-green-500/10 text-green-500 rounded-full text-xs font-medium border border-green-500/20">
                        System Healthy
                    </span>
                </div>
            </div>

            {/* KPI Grid - The "Traffic Light" View */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <KPICard
                    title="Fee Collection"
                    value="85%"
                    trend={12}
                    status="good"
                    icon={DollarSign}
                />
                <KPICard
                    title="Attendance"
                    value="94%"
                    trend={-2}
                    status="warning"
                    icon={Users}
                />
                <KPICard
                    title="Academic Health"
                    value="B+"
                    trend={5}
                    status="good"
                    icon={Activity}
                />
            </div>

            {/* Visual Capitalist Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                {/* Financial Flow */}
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                    <h3 className="text-lg font-semibold text-white mb-6">Financial Trajectory (6 Months)</h3>
                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={MOCK_TREND_DATA}>
                                <defs>
                                    <linearGradient id="colorFees" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#10B981" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                                <XAxis dataKey="name" stroke="#64748b" />
                                <YAxis stroke="#64748b" />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b' }}
                                />
                                <Area
                                    type="monotone"
                                    dataKey="fees"
                                    stroke="#10B981"
                                    fillOpacity={1}
                                    fill="url(#colorFees)"
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Attendance vs Performance */}
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                    <h3 className="text-lg font-semibold text-white mb-6">Attendance vs Grades</h3>
                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={MOCK_TREND_DATA}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                                <XAxis dataKey="name" stroke="#64748b" />
                                <YAxis stroke="#64748b" />
                                <Tooltip
                                    cursor={{ fill: '#1e293b' }}
                                    contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b' }}
                                />
                                <Bar dataKey="attendance" fill="#3B82F6" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* Critical Alerts - "Red Light" Zone */}
            <div className="bg-red-500/5 border border-red-500/20 rounded-2xl p-6">
                <h3 className="text-lg font-semibold text-red-500 flex items-center gap-2 mb-4">
                    <AlertTriangle size={20} />
                    Critical Attention Needed
                </h3>
                <div className="space-y-4">
                    <div className="flex items-start gap-4 p-4 bg-red-500/10 rounded-xl border border-red-500/10">
                        <div className="w-2 h-2 mt-2 rounded-full bg-red-500" />
                        <div>
                            <h4 className="text-white font-medium">Year 6 Math Performance</h4>
                            <p className="text-slate-400 text-sm mt-1">
                                Average score dropped by 15% this month. Recommended Action: Schedule meeting with Dept Head.
                            </p>
                        </div>
                    </div>
                    <div className="flex items-start gap-4 p-4 bg-yellow-500/10 rounded-xl border border-yellow-500/10">
                        <div className="w-2 h-2 mt-2 rounded-full bg-yellow-500" />
                        <div>
                            <h4 className="text-white font-medium">Fee Arrears - Senior 4</h4>
                            <p className="text-slate-400 text-sm mt-1">
                                12 students have outstanding balances &gt; 500k. Recommended Action: Trigger automated SMS reminders.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};
