import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from "recharts";
import { CheckCircle, Clock, Star } from "lucide-react";

const TEACHER_PERFORMANCE = [
    { metric: 'Attendance', value: 98 },
    { metric: 'Syllabus', value: 85 },
    { metric: 'Student Avg', value: 72 },
    { metric: 'Parent Rating', value: 90 },
];

export const StaffProfile = () => {
    return (
        <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-8">
            <div className="flex gap-6 items-center">
                <div className="w-24 h-24 rounded-full bg-blue-600 flex items-center justify-center text-3xl font-bold text-white">
                    JD
                </div>
                <div>
                    <h1 className="text-2xl font-bold text-white">Mr. John Doe</h1>
                    <p className="text-slate-400">Senior Math Teacher • Staff ID: S-101</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                    <h3 className="text-slate-400 text-sm">Classes Taught</h3>
                    <p className="text-3xl font-bold text-white mt-2">4</p>
                    <div className="flex items-center gap-1 text-slate-500 text-sm mt-2">
                        <Clock size={16} /> 24 Hours/Week
                    </div>
                </div>
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                    <h3 className="text-slate-400 text-sm">Task Completion</h3>
                    <p className="text-3xl font-bold text-white mt-2">95%</p>
                    <div className="flex items-center gap-1 text-green-500 text-sm mt-2">
                        <CheckCircle size={16} /> On Track
                    </div>
                </div>
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                    <h3 className="text-slate-400 text-sm">Performance Score</h3>
                    <p className="text-3xl font-bold text-white mt-2">4.8/5</p>
                    <div className="flex items-center gap-1 text-yellow-500 text-sm mt-2">
                        <Star size={16} /> Star Teacher
                    </div>
                </div>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                <h3 className="text-lg font-semibold text-white mb-6">Teacher Performance Metrics (ROI)</h3>
                <div className="h-[300px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={TEACHER_PERFORMANCE} layout="vertical">
                            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                            <XAxis type="number" domain={[0, 100]} stroke="#64748b" />
                            <YAxis dataKey="metric" type="category" stroke="#64748b" width={100} />
                            <Tooltip
                                cursor={{ fill: '#1e293b' }}
                                contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b' }}
                            />
                            <Bar dataKey="value" fill="#8B5CF6" radius={[0, 4, 4, 0]} barSize={20} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
};
