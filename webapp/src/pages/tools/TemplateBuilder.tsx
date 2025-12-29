import { useState } from 'react';
import {
    Layout, Type, Image as ImageIcon, CheckCircle,
    Save, Printer, Palette, Grid, ALargeSmall, Move
} from 'lucide-react';
import clsx from 'clsx';

type TemplateSection = 'header' | 'grades' | 'attendance' | 'comments' | 'footer';

export const TemplateBuilder = () => {
    const [activeSections, setActiveSections] = useState<TemplateSection[]>(['header', 'grades', 'comments']);
    const [primaryColor, setPrimaryColor] = useState('#3B82F6');
    const [schoolName, setSchoolName] = useState('Angels High School');

    // Toggle a section
    const toggleSection = (section: TemplateSection) => {
        if (activeSections.includes(section)) {
            setActiveSections(activeSections.filter(s => s !== section));
        } else {
            setActiveSections([...activeSections, section]);
        }
    };

    return (
        <div className="h-[calc(100vh-64px)] flex text-white overflow-hidden">

            {/* Left Sidebar: Components */}
            <div className="w-64 bg-slate-900 border-r border-slate-800 p-4 flex flex-col gap-4">
                <h2 className="font-bold text-lg mb-2">Components</h2>

                <button
                    onClick={() => toggleSection('header')}
                    className={clsx("flex items-center gap-3 p-3 rounded-xl border transition-all",
                        activeSections.includes('header') ? "bg-indigo-600/20 border-indigo-500 text-indigo-400" : "bg-slate-800 border-slate-700 hover:bg-slate-700"
                    )}
                >
                    <Layout size={20} /> Header (Logo/Name)
                </button>

                <button
                    onClick={() => toggleSection('grades')}
                    className={clsx("flex items-center gap-3 p-3 rounded-xl border transition-all",
                        activeSections.includes('grades') ? "bg-indigo-600/20 border-indigo-500 text-indigo-400" : "bg-slate-800 border-slate-700 hover:bg-slate-700"
                    )}
                >
                    <Grid size={20} /> Grades Table
                </button>

                <button
                    onClick={() => toggleSection('attendance')}
                    className={clsx("flex items-center gap-3 p-3 rounded-xl border transition-all",
                        activeSections.includes('attendance') ? "bg-indigo-600/20 border-indigo-500 text-indigo-400" : "bg-slate-800 border-slate-700 hover:bg-slate-700"
                    )}
                >
                    <CheckCircle size={20} /> Attendance Summary
                </button>

                <button
                    onClick={() => toggleSection('comments')}
                    className={clsx("flex items-center gap-3 p-3 rounded-xl border transition-all",
                        activeSections.includes('comments') ? "bg-indigo-600/20 border-indigo-500 text-indigo-400" : "bg-slate-800 border-slate-700 hover:bg-slate-700"
                    )}
                >
                    <Type size={20} /> Teacher Comments
                </button>

                <div className="mt-8 border-t border-slate-800 pt-4">
                    <h2 className="font-bold text-lg mb-2">Style</h2>
                    <div className="flex flex-col gap-3">
                        <label className="text-sm text-slate-400">Primary Color</label>
                        <input
                            type="color"
                            value={primaryColor}
                            onChange={(e) => setPrimaryColor(e.target.value)}
                            className="w-full h-10 rounded cursor-pointer bg-transparent"
                        />
                        <label className="text-sm text-slate-400">School Name Preview</label>
                        <input
                            type="text"
                            value={schoolName}
                            onChange={(e) => setSchoolName(e.target.value)}
                            className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-sm"
                        />
                    </div>
                </div>
            </div>

            {/* Main Area: Live Preview */}
            <div className="flex-1 bg-slate-950 p-8 flex justify-center overflow-y-auto">
                <div
                    className="bg-white text-slate-900 w-[210mm] min-h-[297mm] shadow-2xl p-8 flex flex-col gap-6 relative"
                    id="report-card-preview"
                >
                    {/* Header */}
                    {activeSections.includes('header') && (
                        <div className="border-b-2 pb-4 flex items-center justify-between" style={{ borderColor: primaryColor }}>
                            <div className="flex items-center gap-4">
                                <div className="w-20 h-20 bg-slate-200 rounded-full flex items-center justify-center text-slate-400">
                                    <ImageIcon size={32} />
                                </div>
                                <div>
                                    <h1 className="text-3xl font-bold uppercase tracking-wide" style={{ color: primaryColor }}>{schoolName}</h1>
                                    <p className="text-sm text-slate-500">Excellence in Technology & Integrity</p>
                                </div>
                            </div>
                            <div className="text-right text-sm text-slate-500">
                                <p>End of Term 3, 2025</p>
                                <p>Student: <strong>John Doe</strong></p>
                            </div>
                        </div>
                    )}

                    {/* Grades */}
                    {activeSections.includes('grades') && (
                        <div className="flex-1">
                            <h3 className="font-bold text-lg mb-2 uppercase border-l-4 pl-2" style={{ borderColor: primaryColor }}>Academic Performance</h3>
                            <table className="w-full text-sm border-collapse">
                                <thead>
                                    <tr className="bg-slate-100 border-b-2 border-slate-300">
                                        <th className="p-2 text-left">Subject</th>
                                        <th className="p-2 text-center">Score</th>
                                        <th className="p-2 text-center">Grade</th>
                                        <th className="p-2 text-left">Remarks</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {[
                                        { sub: 'Mathematics', score: 92, grade: 'D1' },
                                        { sub: 'English', score: 85, grade: 'D1' },
                                        { sub: 'Integrated Science', score: 78, grade: 'D2' },
                                        { sub: 'Social Studies', score: 88, grade: 'D1' }
                                    ].map((row, i) => (
                                        <tr key={i} className="border-b border-slate-200">
                                            <td className="p-3 font-medium">{row.sub}</td>
                                            <td className="p-3 text-center">{row.score}</td>
                                            <td className="p-3 text-center font-bold" style={{ color: primaryColor }}>{row.grade}</td>
                                            <td className="p-3 text-slate-600">Excellent performance, keep it up.</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}

                    {/* Attendance */}
                    {activeSections.includes('attendance') && (
                        <div className="p-4 bg-slate-100 rounded-lg flex items-center justify-between">
                            <div>
                                <h3 className="font-bold uppercase text-sm mb-1" style={{ color: primaryColor }}>Attendance Record</h3>
                                <p className="text-xs text-slate-500">Total Days Present</p>
                            </div>
                            <div className="text-2xl font-bold">88 / 90 Days</div>
                        </div>
                    )}

                    {/* Comments */}
                    {activeSections.includes('comments') && (
                        <div className="mt-4 border p-4 rounded-lg border-slate-300 border-dashed">
                            <h3 className="font-bold uppercase text-sm mb-2" style={{ color: primaryColor }}>Class Teacher's Comment</h3>
                            <p className="font-serif italic text-slate-700">
                                "John has shown remarkable improvement in Mathematics this term. He is a disciplined and active member of the class."
                            </p>
                            <div className="mt-8 flex justify-end">
                                <div className="border-t border-slate-400 w-48 pt-2 text-center text-xs text-slate-500">
                                    Signature
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Footer */}
                    <div className="mt-auto text-center text-xs text-slate-400 pt-8 border-t">
                        Generated by Angels AI School Operating System
                    </div>

                </div>
            </div>

            {/* Right Sidebar: Actions */}
            <div className="w-64 bg-slate-900 border-l border-slate-800 p-4">
                <h2 className="font-bold text-lg mb-4">Actions</h2>
                <div className="space-y-3">
                    <button className="w-full bg-green-600 hover:bg-green-500 text-white p-3 rounded-xl font-medium flex items-center justify-center gap-2">
                        <Save size={20} /> Save Template
                    </button>
                    <button className="w-full bg-indigo-600 hover:bg-indigo-500 text-white p-3 rounded-xl font-medium flex items-center justify-center gap-2">
                        <Printer size={20} /> Print Sample
                    </button>
                    <div className="border-t border-slate-800 my-4"></div>
                    <p className="text-xs text-slate-400">
                        This template will be applied to all 450 students when generating End of Term reports.
                    </p>
                </div>
            </div>
        </div>
    );
};
