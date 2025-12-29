import {
    RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer
} from "recharts";
import { Smile, Frown, DollarSign } from "lucide-react";

const WELLBEING_DATA = [
    { subject: 'Academic', A: 120, fullMark: 150 },
    { subject: 'Social', A: 98, fullMark: 150 },
    { subject: 'Health', A: 86, fullMark: 150 },
    { subject: 'Discipline', A: 99, fullMark: 150 },
    { subject: 'Sports', A: 85, fullMark: 150 },
    { subject: 'Art', A: 65, fullMark: 150 },
];

export const StudentProfile = () => {
    // Ideally receives student ID from params
    return (
        <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-8">
            <div className="flex gap-6 items-center">
                <img
                    src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix"
                    alt="Student"
                    className="w-24 h-24 rounded-full border-4 border-slate-800 bg-slate-800"
                />
                <div>
                    <h1 className="text-2xl font-bold text-white">Felix K.</h1>
                    <p className="text-slate-400">Class 5A • ID: 2024001</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                {/* Wellbeing 360 - The "Spider" Chart */}
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                    <h3 className="text-lg font-semibold text-white mb-6">360° Student Pulse</h3>
                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <RadarChart cx="50%" cy="50%" outerRadius="80%" data={WELLBEING_DATA}>
                                <PolarGrid stroke="#1e293b" />
                                <PolarAngleAxis dataKey="subject" stroke="#94a3b8" />
                                <PolarRadiusAxis angle={30} domain={[0, 150]} stroke="#1e293b" />
                                <Radar
                                    name="Felix"
                                    dataKey="A"
                                    stroke="#8884d8"
                                    fill="#8884d8"
                                    fillOpacity={0.6}
                                />
                            </RadarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* AI Mental Health / Chatbot Analysis */}
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                    <h3 className="text-lg font-semibold text-white mb-4">Wellbeing & Survey Analysis</h3>

                    <div className="space-y-4">
                        <div className="p-4 bg-slate-950 rounded-xl border border-slate-800">
                            <div className="flex items-center gap-2 mb-2">
                                <Smile className="text-green-500" size={20} />
                                <h4 className="font-medium text-white">Positive Sentiment</h4>
                            </div>
                            <p className="text-slate-400 text-sm">
                                Analysis of recent chatbot interactions shows high engagement in Sports and Science. Felix seems happy but mentioned "Math is getting harder".
                            </p>
                        </div>

                        <div className="p-4 bg-slate-950 rounded-xl border border-slate-800">
                            <div className="flex items-center gap-2 mb-2">
                                <DollarSign className="text-yellow-500" size={20} />
                                <h4 className="font-medium text-white">Fee Status</h4>
                            </div>
                            <p className="text-slate-400 text-sm">
                                Balance: <strong>50,000 UGX</strong>. Next installment due in 14 days. Parent has been notified via WhatsApp.
                            </p>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    );
};
