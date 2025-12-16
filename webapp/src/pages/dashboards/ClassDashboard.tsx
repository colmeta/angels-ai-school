import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from "recharts";
import { TrendingUp, Users, BookOpen } from "lucide-react";
import clsx from "clsx";

const MOCK_CLASS_DATA = [
    { term: 'Term 1', math: 65, science: 70, english: 75 },
    { term: 'Term 2', math: 68, science: 72, english: 74 },
    { term: 'Term 3', math: 75, science: 78, english: 80 },
];

export const ClassDashboard = () => {
    return (
        <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-8">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-white">Class 5A Overview</h1>
                    <p className="text-slate-400">Class Teacher: Mr. Okello</p>
                </div>
                <div className="flex gap-2">
                    <span className="px-3 py-1 bg-blue-500/10 text-blue-500 rounded-full text-xs font-medium border border-blue-500/20">
                        Trajectory: UP ↗
                    </span>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                    <h3 className="text-slate-400 text-sm">Class Average</h3>
                    <p className="text-3xl font-bold text-white mt-2">72%</p>
                    <div className="flex items-center gap-1 text-green-500 text-sm mt-2">
                        <TrendingUp size={16} /> +4% vs Last Term
                    </div>
                </div>
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                    <h3 className="text-slate-400 text-sm">Students</h3>
                    <p className="text-3xl font-bold text-white mt-2">45</p>
                    <div className="flex items-center gap-1 text-slate-500 text-sm mt-2">
                        <Users size={16} /> Full Capacity
                    </div>
                </div>
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                    <h3 className="text-slate-400 text-sm">Top Subject</h3>
                    <p className="text-3xl font-bold text-white mt-2">English</p>
                    <div className="flex items-center gap-1 text-blue-500 text-sm mt-2">
                        <BookOpen size={16} /> 80% Avg
                    </div>
                </div>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                <h3 className="text-lg font-semibold text-white mb-6">Subject Performance Trajectory</h3>
                <div className="h-[300px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={MOCK_CLASS_DATA}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                            <XAxis dataKey="term" stroke="#64748b" />
                            <YAxis stroke="#64748b" />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b' }}
                            />
                            <Line type="monotone" dataKey="math" stroke="#EF4444" strokeWidth={2} />
                            <Line type="monotone" dataKey="science" stroke="#10B981" strokeWidth={2} />
                            <Line type="monotone" dataKey="english" stroke="#3B82F6" strokeWidth={2} />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
};
