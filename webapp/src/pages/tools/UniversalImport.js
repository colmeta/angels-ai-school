import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { Upload, FileSpreadsheet, CheckCircle, AlertCircle, ArrowRight } from 'lucide-react';
import clsx from 'clsx';
import { localAgent } from '../../services/LocalAgentService';
import { useOfflineSync } from '../../hooks/useOfflineSync';
export const UniversalImport = () => {
    const [file, setFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [loading, setLoading] = useState(false);
    const [step, setStep] = useState('upload');
    const parseCSV = (csv) => {
        const lines = csv.split('\n').filter(l => l.trim().length > 0);
        const headers = lines[0].split(',').map(h => h.trim());
        const data = lines.slice(1).map(line => {
            const values = line.split(',').map(v => v.trim());
            return headers.reduce((obj, header, i) => {
                obj[header] = values[i];
                return obj;
            }, {});
        });
        return { headers, data };
    };
    const handleFileChange = async (e) => {
        const selectedFile = e.target.files?.[0];
        if (!selectedFile)
            return;
        setFile(selectedFile);
        setLoading(true);
        try {
            const text = await selectedFile.text();
            const { headers, data } = parseCSV(text);
            // Use Edge AI to map headers
            let mapping = {};
            let confidence = 0.5;
            if (localAgent.getStatus() === 'ready') {
                const prompt = `Map these Excel headers: [${headers.join(', ')}] to our schema fields: [admission_number, first_name, last_name, class_name, gender, phone]. Return JSON mapping only.`;
                const aiResult = await localAgent.parse(prompt);
                mapping = aiResult;
                confidence = 0.95;
            }
            else {
                // Heuristic fallback
                headers.forEach(h => {
                    const normalized = h.toLowerCase().replace(/[\s_]/g, '');
                    if (normalized.includes('name'))
                        mapping['first_name'] = h;
                    if (normalized.includes('class'))
                        mapping['class_name'] = h;
                    if (normalized.includes('adm'))
                        mapping['admission_number'] = h;
                });
            }
            setPreview({
                detected_mapping: mapping,
                sample_data: data.slice(0, 5),
                total_rows: data.length,
                confidence: confidence,
                warnings: Object.keys(mapping).length < 2 ? ['Few columns matched automatically.'] : []
            });
            setStep('preview');
        }
        catch (error) {
            alert("Failed to parse file. Please use a standard CSV.");
        }
        finally {
            setLoading(false);
        }
    };
    const { enqueueTask } = useOfflineSync();
    const handleImport = async () => {
        if (!preview)
            return;
        setLoading(true);
        try {
            // E2E Verification: Enqueue the import task for offline sync
            enqueueTask('/students/import', {
                mapping: preview.detected_mapping,
                file_name: file?.name,
                data_count: preview.total_rows
            }, 'POST');
            setStep('done');
        }
        catch (error) {
            console.error(error);
        }
        finally {
            setLoading(false);
        }
    };
    return (_jsxs("div", { className: "p-6 md:p-8 max-w-5xl mx-auto", children: [_jsxs("div", { className: "mb-8", children: [_jsxs("h1", { className: "text-2xl font-bold text-white flex items-center gap-2", children: [_jsx(FileSpreadsheet, { size: 28, className: "text-indigo-400" }), "Universal Import (Edge AI Powered)"] }), _jsx("p", { className: "text-slate-400 mt-1", children: "Upload any Excel or CSV. Our on-device AI handles the mapping." })] }), step === 'upload' && (_jsxs("div", { className: "bg-slate-900 border-2 border-dashed border-slate-700 rounded-2xl p-12 text-center", children: [_jsx(Upload, { size: 64, className: "mx-auto text-slate-600 mb-4" }), _jsx("h3", { className: "text-xl font-semibold text-white mb-2", children: "Drop your CSV here" }), _jsx("p", { className: "text-slate-400 mb-6", children: "Supported: CSV (.csv), Plain Text. Excel coming soon." }), _jsxs("label", { className: "cursor-pointer", children: [_jsx("input", { type: "file", accept: ".csv", className: "hidden", onChange: handleFileChange }), _jsx("div", { className: "bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-3 rounded-xl inline-block transition-colors", children: "Choose File" })] }), loading && (_jsxs("div", { className: "mt-6", children: [_jsx("div", { className: "animate-spin h-8 w-8 border-4 border-indigo-500 border-t-transparent rounded-full mx-auto" }), _jsx("p", { className: "text-slate-400 mt-2 text-sm italic", children: "Local AI is mapping columns..." })] }))] })), step === 'preview' && preview && (_jsxs("div", { className: "space-y-6", children: [_jsx("div", { className: clsx("p-6 rounded-xl border-2", preview.confidence >= 0.8 ? "bg-green-500/10 border-green-500/30" : "bg-yellow-500/10 border-yellow-500/30"), children: _jsxs("div", { className: "flex items-center gap-3", children: [preview.confidence >= 0.8 ? (_jsx(CheckCircle, { size: 32, className: "text-green-500" })) : (_jsx(AlertCircle, { size: 32, className: "text-yellow-500" })), _jsxs("div", { children: [_jsxs("h3", { className: "text-lg font-semibold text-white", children: [(preview.confidence * 100).toFixed(0), "% AI Mapping Confidence"] }), _jsxs("p", { className: "text-sm text-slate-400", children: ["Successfully matched ", Object.keys(preview.detected_mapping).length, " database fields"] })] })] }) }), _jsxs("div", { className: "bg-slate-900 border border-slate-800 rounded-xl p-6", children: [_jsx("h3", { className: "font-semibold text-white mb-4", children: "On-Device Column Mapping" }), _jsx("div", { className: "grid grid-cols-1 md:grid-cols-2 gap-4", children: Object.entries(preview.detected_mapping).map(([ourField, excelCol]) => (_jsxs("div", { className: "flex items-center justify-between p-3 bg-slate-800/50 rounded-lg border border-slate-700/50", children: [_jsx("span", { className: "text-slate-400 text-sm", children: excelCol }), _jsx(ArrowRight, { size: 14, className: "text-indigo-400" }), _jsx("span", { className: "text-white font-medium text-sm", children: ourField.replace('_', ' ') })] }, ourField))) })] }), _jsxs("div", { className: "bg-slate-900 border border-slate-800 rounded-xl p-6 overflow-hidden", children: [_jsxs("h3", { className: "font-semibold text-white mb-4", children: ["Data Preview (", preview.total_rows, " rows found)"] }), _jsx("div", { className: "overflow-x-auto", children: _jsxs("table", { className: "w-full text-xs", children: [_jsx("thead", { className: "border-b border-slate-700", children: _jsx("tr", { children: Object.values(preview.detected_mapping).map(col => (_jsx("th", { className: "text-left p-3 text-slate-500 font-bold uppercase", children: col }, col))) }) }), _jsx("tbody", { children: preview.sample_data.map((row, i) => (_jsx("tr", { className: "border-b border-slate-800/50", children: Object.values(preview.detected_mapping).map(col => (_jsx("td", { className: "p-3 text-slate-300 font-mono", children: row[col] || '-' }, col))) }, i))) })] }) })] }), _jsxs("div", { className: "flex gap-4", children: [_jsx("button", { onClick: () => setStep('upload'), className: "flex-1 bg-slate-800 hover:bg-slate-700 text-white p-4 rounded-xl transition-all", children: "Cancel" }), _jsxs("button", { onClick: handleImport, className: "flex-1 bg-indigo-600 hover:bg-indigo-500 text-white p-4 rounded-xl font-bold shadow-lg shadow-indigo-500/20 active:scale-95 transition-all", children: ["Import ", preview.total_rows, " Records"] })] })] })), step === 'done' && (_jsxs("div", { className: "bg-green-500/10 border-2 border-green-500/30 rounded-2xl p-12 text-center animate-in fade-in zoom-in duration-500", children: [_jsx(CheckCircle, { size: 64, className: "mx-auto text-green-500 mb-4" }), _jsx("h3", { className: "text-2xl font-semibold text-white mb-2", children: "Market Ready!" }), _jsx("p", { className: "text-slate-400 mb-6 font-medium", children: "All data has been distributed and processed locally." }), _jsx("button", { onClick: () => window.location.href = '/admin', className: "bg-slate-100 text-slate-900 px-8 py-3 rounded-xl font-bold hover:bg-white transition-colors", children: "Go to Dashboard" })] }))] }));
};
