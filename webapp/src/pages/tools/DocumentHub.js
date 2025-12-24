import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useState } from "react";
import { CreditCard, FileText, LogOut, Download, UserPlus, Printer, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { apiClient } from "../../lib/apiClient";
import { useBrandingStore } from "../../stores/branding";
export const DocumentHub = () => {
    const { schoolId, displayName } = useBrandingStore();
    const [selectedType, setSelectedType] = useState("id-card");
    const [isGenerating, setIsGenerating] = useState(false);
    const [status, setStatus] = useState(null);
    // Form states
    const [studentName, setStudentName] = useState("");
    const [studentId, setStudentId] = useState("");
    const [className, setClassName] = useState("Grade 5A");
    const [reason, setReason] = useState("");
    const [departureTime, setDepartureTime] = useState("");
    const handleGenerate = async () => {
        setIsGenerating(true);
        setStatus(null);
        try {
            let endpoint = "";
            let payload = {};
            let filename = "document.png";
            if (selectedType === "id-card") {
                endpoint = "/documents/id-cards/student";
                payload = {
                    student_name: studentName || "John Doe",
                    student_id: studentId || "STU-001",
                    class_name: className,
                    school_name: displayName || "Angels AI School"
                };
                filename = `id_card_${studentId || 'sample'}.png`;
            }
            else if (selectedType === "report-card") {
                endpoint = "/documents/report-cards/generate";
                payload = {
                    student_name: studentName || "John Doe",
                    student_id: studentId || "STU-001",
                    class_name: className,
                    term: "Term 1",
                    year: "2024",
                    school_name: displayName || "Angels AI School",
                    school_address: "Education Street, Kampala",
                    subjects: [
                        { name: "Mathematics", score: 85, grade: "A", remarks: "Excellent" },
                        { name: "English", score: 78, grade: "B+", remarks: "Very Good" },
                        { name: "Science", score: 92, grade: "A+", remarks: "Outstanding" }
                    ]
                };
                filename = `report_card_${studentId || 'sample'}.png`;
            }
            else {
                endpoint = "/documents/pass-out-slips/generate";
                payload = {
                    student_name: studentName || "John Doe",
                    student_id: studentId || "STU-001",
                    class_name: className,
                    reason: reason || "Parental Request",
                    departure_time: departureTime || "10:00 AM",
                    authorized_by: "School Office",
                    school_name: displayName || "Angels AI School"
                };
                filename = `pass_out_${studentId || 'sample'}.png`;
            }
            const response = await apiClient.post(endpoint, payload, {
                responseType: 'blob'
            });
            // Create download link
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', filename);
            document.body.appendChild(link);
            link.click();
            link.remove();
            setStatus({ type: 'success', message: `${filename} generated successfully!` });
        }
        catch (error) {
            console.error("Generation error:", error);
            setStatus({ type: 'error', message: "Failed to generate document. Please check your inputs." });
        }
        finally {
            setIsGenerating(false);
        }
    };
    return (_jsxs("div", { className: "p-6 max-w-5xl mx-auto space-y-8", children: [_jsxs("header", { className: "space-y-2", children: [_jsx("h1", { className: "text-3xl font-bold text-white", children: "Document Hub" }), _jsx("p", { className: "text-slate-400", children: "Generate high-quality, 300 DPI printable documents for your school instantly." })] }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-3 gap-4", children: [_jsx(DocTypeCard, { active: selectedType === "id-card", onClick: () => setSelectedType("id-card"), icon: CreditCard, title: "ID Cards", description: "Professional photo IDs for students and staff." }), _jsx(DocTypeCard, { active: selectedType === "report-card", onClick: () => setSelectedType("report-card"), icon: FileText, title: "Report Cards", description: "Printable academic reports with student photos." }), _jsx(DocTypeCard, { active: selectedType === "pass-out", onClick: () => setSelectedType("pass-out"), icon: LogOut, title: "Pass-out Slips", description: "Security-verified slips for students leaving school." })] }), _jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-2 gap-8", children: [_jsxs("div", { className: "bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-6", children: [_jsxs("h2", { className: "text-xl font-semibold flex items-center gap-2", children: [_jsx(UserPlus, { size: 20, className: "text-blue-500" }), "Enter Details"] }), _jsxs("div", { className: "space-y-4", children: [_jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-slate-400 mb-1", children: "Student/Staff Name" }), _jsx("input", { type: "text", value: studentName, onChange: (e) => setStudentName(e.target.value), placeholder: "Full Name", className: "w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2 text-white focus:ring-2 focus:ring-blue-500 transition-all" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-slate-400 mb-1", children: "Registration ID" }), _jsx("input", { type: "text", value: studentId, onChange: (e) => setStudentId(e.target.value), placeholder: "ID Number", className: "w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2 text-white focus:ring-2 focus:ring-blue-500 transition-all" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-slate-400 mb-1", children: "Class/Grade" }), _jsxs("select", { value: className, onChange: (e) => setClassName(e.target.value), className: "w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2 text-white focus:ring-2 focus:ring-blue-500 transition-all", children: [_jsx("option", { children: "Grade 1" }), _jsx("option", { children: "Grade 2" }), _jsx("option", { children: "Grade 3" }), _jsx("option", { children: "Grade 4" }), _jsx("option", { children: "Grade 5A" }), _jsx("option", { children: "Grade 5B" }), _jsx("option", { children: "Grade 6" }), _jsx("option", { children: "Grade 7" })] })] }), selectedType === "pass-out" && (_jsxs(motion.div, { initial: { opacity: 0, height: 0 }, animate: { opacity: 1, height: "auto" }, className: "space-y-4", children: [_jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-slate-400 mb-1", children: "Reason for Leaving" }), _jsx("input", { type: "text", value: reason, onChange: (e) => setReason(e.target.value), placeholder: "E.g. Sick, Family Event", className: "w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2 text-white" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-slate-400 mb-1", children: "Departure Time" }), _jsx("input", { type: "text", value: departureTime, onChange: (e) => setDepartureTime(e.target.value), placeholder: "E.g. 10:30 AM", className: "w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2 text-white" })] })] }))] }), _jsx("button", { onClick: handleGenerate, disabled: isGenerating, className: "w-full bg-blue-600 hover:bg-blue-500 py-3 rounded-xl font-bold flex items-center justify-center gap-2 transition-all shadow-lg shadow-blue-500/20", children: isGenerating ? (_jsxs(_Fragment, { children: [_jsx(Loader2, { className: "animate-spin" }), "Generating..."] })) : (_jsxs(_Fragment, { children: [_jsx(Download, {}), "Download Printable PNG"] })) }), _jsx(AnimatePresence, { children: status && (_jsxs(motion.div, { initial: { opacity: 0, y: 10 }, animate: { opacity: 1, y: 0 }, exit: { opacity: 0 }, className: `p-4 rounded-xl flex items-center gap-3 ${status.type === 'success' ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20' : 'bg-red-500/10 text-red-500 border border-red-500/20'}`, children: [status.type === 'success' ? _jsx(CheckCircle2, { size: 18 }) : _jsx(AlertCircle, { size: 18 }), _jsx("span", { className: "text-sm", children: status.message })] })) })] }), _jsxs("div", { className: "bg-slate-950 border border-slate-800 rounded-2xl p-6 flex flex-col items-center justify-center text-center space-y-4", children: [_jsx("div", { className: "w-16 h-16 bg-slate-900 rounded-full flex items-center justify-center text-slate-500", children: _jsx(Printer, { size: 32 }) }), _jsxs("div", { children: [_jsx("h3", { className: "text-lg font-semibold", children: "Print-Ready Quality" }), _jsx("p", { className: "text-sm text-slate-500 max-w-xs mx-auto", children: "All documents are generated at 300 DPI. Perfect for laser or inkjet printing on standard paper or PVC card printers." })] })] })] })] }));
};
const DocTypeCard = ({ active, onClick, icon: Icon, title, description }) => (_jsxs("button", { onClick: onClick, className: `p-5 rounded-2xl border-2 text-left transition-all ${active
        ? "bg-blue-600/10 border-blue-600 shadow-lg shadow-blue-900/20"
        : "bg-slate-900/40 border-slate-800 hover:border-slate-700"}`, children: [_jsx("div", { className: `w-10 h-10 rounded-xl flex items-center justify-center mb-4 ${active ? "bg-blue-600 text-white" : "bg-slate-800 text-slate-400"}`, children: _jsx(Icon, { size: 20 }) }), _jsx("h3", { className: `font-bold ${active ? "text-white" : "text-slate-200"}`, children: title }), _jsx("p", { className: "text-xs text-slate-500 mt-1", children: description })] }));
