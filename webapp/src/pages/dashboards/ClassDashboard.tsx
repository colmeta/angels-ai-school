/**
 * Class Dashboard (Teacher View)
 * ==============================
 * Real-time academic performance tracking.
 * CONNECTED TO: api/routes/analytics.py
 */
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from "recharts";
import { Users, BookOpen, AlertTriangle } from "lucide-react";
import clsx from "clsx";

import { apiClient } from "../../lib/apiClient";
import { useBrandingStore } from "../../stores/branding";

export const ClassDashboard = () => {
    const schoolId = useBrandingStore(state => state.schoolId) || "demo-school";
    const [selectedClass, setSelectedClass] = useState("Grade 10-A"); // Default or fetch from teacher profile

    // Fetch Real Analytics Data
    const { data: analytics, isLoading } = useQuery({
        queryKey: ["class-analytics", schoolId, selectedClass],
        queryFn: async () => {
            const res = await apiClient.get(`/${schoolId}/analytics/academic?class_name=${selectedClass}`);
            return res.data;
        }
    });

    const subjectPerformance = analytics?.subject_performance || [];
    const decliningStudents = analytics?.declining_students || [];

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-6">
            <header className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-slate-800 dark:text-white">Class Performance</h1>
                    <p className="text-slate-500">Real-time academic analysis for {selectedClass}</p>
                </div>
                <select
                    value={selectedClass}
                    onChange={(e) => setSelectedClass(e.target.value)}
                    className="p-2 border rounded-lg bg-white dark:bg-slate-800 dark:text-white"
                >
                    <option>Grade 10-A</option>
                    <option>Grade 10-B</option>
                    <option>Grade 11-Science</option>
                </select>
            </header>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
                    <div className="flex items-center gap-4">
                        <div className="p-3 bg-blue-100 text-blue-600 rounded-lg">
                            <BookOpen size={24} />
                        </div>
                        <div>
                            <p className="text-sm text-slate-500">Subject Average</p>
                            <h3 className="text-2xl font-bold dark:text-white">
                                {subjectPerformance.length > 0
                                    ? Math.round(subjectPerformance.reduce((acc: any, curr: any) => acc + curr.avg_percentage, 0) / subjectPerformance.length)
                                    : 0}%
                            </h3>
                        </div>
                    </div>
                </div>
                <div className="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
                    <div className="flex items-center gap-4">
                        <div className="p-3 bg-amber-100 text-amber-600 rounded-lg">
                            <AlertTriangle size={24} />
                        </div>
                        <div>
                            <p className="text-sm text-slate-500">Students At Risk</p>
                            <h3 className="text-2xl font-bold dark:text-white text-amber-500">
                                {decliningStudents.length}
                            </h3>
                        </div>
                    </div>
                </div>
            </div>

            {/* Performance Chart */}
            <div className="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm h-[400px]">
                <h3 className="text-lg font-bold mb-4 dark:text-white">Subject Performance</h3>
                {isLoading ? (
                    <div className="h-full flex items-center justify-center text-slate-400">Loading Analysis...</div>
                ) : subjectPerformance.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={subjectPerformance}>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                            <XAxis dataKey="subject" />
                            <YAxis domain={[0, 100]} />
                            <Tooltip
                                contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                            />
                            <Bar
                                dataKey="avg_percentage"
                                fill="#4F46E5"
                                radius={[4, 4, 0, 0]}
                                barSize={50}
                            />
                        </BarChart>
                    </ResponsiveContainer>
                ) : (
                    <div className="h-full flex items-center justify-center text-slate-400">
                        No assessment data available for this class period.
                    </div>
                )}
            </div>

            {/* At Risk List */}
            {decliningStudents.length > 0 && (
                <div className="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
                    <h3 className="text-lg font-bold mb-4 text-red-500 flex items-center gap-2">
                        <AlertTriangle size={20} /> Attention Required
                    </h3>
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="border-b dark:border-slate-800 text-slate-500 text-sm">
                                    <th className="p-3">Student</th>
                                    <th className="p-3">Trend</th>
                                    <th className="p-3">Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {decliningStudents.map((student: any) => (
                                    <tr key={student.id} className="border-b dark:border-slate-800 last:border-0 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
                                        <td className="p-3 font-medium dark:text-white">
                                            {student.first_name} {student.last_name}
                                        </td>
                                        <td className="p-3 text-red-500">
                                            {student.change}% Decline
                                        </td>
                                        <td className="p-3">
                                            <button className="text-xs bg-indigo-50 text-indigo-600 px-3 py-1 rounded-full font-semibold hover:bg-indigo-100 transition-colors">
                                                Schedule Meeting
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
};
