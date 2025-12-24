import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * Class Dashboard (Teacher View)
 * ==============================
 * Real-time academic performance tracking.
 * CONNECTED TO: api/routes/analytics.py
 */
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { BookOpen, AlertTriangle } from "lucide-react";
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
    return (_jsxs("div", { className: "p-6 max-w-7xl mx-auto space-y-6", children: [_jsxs("header", { className: "flex justify-between items-center", children: [_jsxs("div", { children: [_jsx("h1", { className: "text-2xl font-bold text-slate-800 dark:text-white", children: "Class Performance" }), _jsxs("p", { className: "text-slate-500", children: ["Real-time academic analysis for ", selectedClass] })] }), _jsxs("select", { value: selectedClass, onChange: (e) => setSelectedClass(e.target.value), className: "p-2 border rounded-lg bg-white dark:bg-slate-800 dark:text-white", children: [_jsx("option", { children: "Grade 10-A" }), _jsx("option", { children: "Grade 10-B" }), _jsx("option", { children: "Grade 11-Science" })] })] }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-3 gap-4", children: [_jsx("div", { className: "bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm", children: _jsxs("div", { className: "flex items-center gap-4", children: [_jsx("div", { className: "p-3 bg-blue-100 text-blue-600 rounded-lg", children: _jsx(BookOpen, { size: 24 }) }), _jsxs("div", { children: [_jsx("p", { className: "text-sm text-slate-500", children: "Subject Average" }), _jsxs("h3", { className: "text-2xl font-bold dark:text-white", children: [subjectPerformance.length > 0
                                                    ? Math.round(subjectPerformance.reduce((acc, curr) => acc + curr.avg_percentage, 0) / subjectPerformance.length)
                                                    : 0, "%"] })] })] }) }), _jsx("div", { className: "bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm", children: _jsxs("div", { className: "flex items-center gap-4", children: [_jsx("div", { className: "p-3 bg-amber-100 text-amber-600 rounded-lg", children: _jsx(AlertTriangle, { size: 24 }) }), _jsxs("div", { children: [_jsx("p", { className: "text-sm text-slate-500", children: "Students At Risk" }), _jsx("h3", { className: "text-2xl font-bold dark:text-white text-amber-500", children: decliningStudents.length })] })] }) })] }), _jsxs("div", { className: "bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm h-[400px]", children: [_jsx("h3", { className: "text-lg font-bold mb-4 dark:text-white", children: "Subject Performance" }), isLoading ? (_jsx("div", { className: "h-full flex items-center justify-center text-slate-400", children: "Loading Analysis..." })) : subjectPerformance.length > 0 ? (_jsx(ResponsiveContainer, { width: "100%", height: "100%", children: _jsxs(BarChart, { data: subjectPerformance, children: [_jsx(CartesianGrid, { strokeDasharray: "3 3", vertical: false, stroke: "#E2E8F0" }), _jsx(XAxis, { dataKey: "subject" }), _jsx(YAxis, { domain: [0, 100] }), _jsx(Tooltip, { contentStyle: { borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' } }), _jsx(Bar, { dataKey: "avg_percentage", fill: "#4F46E5", radius: [4, 4, 0, 0], barSize: 50 })] }) })) : (_jsx("div", { className: "h-full flex items-center justify-center text-slate-400", children: "No assessment data available for this class period." }))] }), decliningStudents.length > 0 && (_jsxs("div", { className: "bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm", children: [_jsxs("h3", { className: "text-lg font-bold mb-4 text-red-500 flex items-center gap-2", children: [_jsx(AlertTriangle, { size: 20 }), " Attention Required"] }), _jsx("div", { className: "overflow-x-auto", children: _jsxs("table", { className: "w-full text-left border-collapse", children: [_jsx("thead", { children: _jsxs("tr", { className: "border-b dark:border-slate-800 text-slate-500 text-sm", children: [_jsx("th", { className: "p-3", children: "Student" }), _jsx("th", { className: "p-3", children: "Trend" }), _jsx("th", { className: "p-3", children: "Action" })] }) }), _jsx("tbody", { children: decliningStudents.map((student) => (_jsxs("tr", { className: "border-b dark:border-slate-800 last:border-0 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors", children: [_jsxs("td", { className: "p-3 font-medium dark:text-white", children: [student.first_name, " ", student.last_name] }), _jsxs("td", { className: "p-3 text-red-500", children: [student.change, "% Decline"] }), _jsx("td", { className: "p-3", children: _jsx("button", { className: "text-xs bg-indigo-50 text-indigo-600 px-3 py-1 rounded-full font-semibold hover:bg-indigo-100 transition-colors", children: "Schedule Meeting" }) })] }, student.id))) })] }) })] }))] }));
};
