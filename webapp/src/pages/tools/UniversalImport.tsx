import { useState } from 'react';
import { Upload, FileSpreadsheet, CheckCircle, AlertCircle, ArrowRight } from 'lucide-react';
import clsx from 'clsx';

interface ImportPreview {
    detected_mapping: Record<string, string>;
    sample_data: any[];
    total_rows: number;
    confidence: number;
    warnings: string[];
}

export const UniversalImport = () => {
    const [file, setFile] = useState<File | null>(null);
    const [preview, setPreview] = useState<ImportPreview | null>(null);
    const [loading, setLoading] = useState(false);
    const [step, setStep] = useState<'upload' | 'preview' | 'done'>('upload');

    const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0];
        if (!selectedFile) return;

        setFile(selectedFile);
        setLoading(true);

        // Mock preview (replace with actual API call)
        setTimeout(() => {
            setPreview({
                detected_mapping: {
                    'admission_number': 'Admno',
                    'first_name': 'Student Name',
                    'class_name': 'Class',
                    'gender': 'Sex'
                },
                sample_data: [
                    { admission_number: 'S001', first_name: 'John Doe', class_name: 'P.5', gender: 'Male' },
                    { admission_number: 'S002', first_name: 'Jane Smith', class_name: 'P.5', gender: 'Female' }
                ],
                total_rows: 250,
                confidence: 0.85,
                warnings: ['Missing field: last_name']
            });
            setStep('preview');
            setLoading(false);
        }, 2000);
    };

    const handleImport = () => {
        setLoading(true);
        // Mock import (replace with actual API call)
        setTimeout(() => {
            setStep('done');
            setLoading(false);
        }, 3000);
    };

    return (
        <div className="p-6 md:p-8 max-w-5xl mx-auto">
            <div className="mb-8">
                <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                    <FileSpreadsheet size={28} className="text-indigo-400" />
                    Universal Import
                </h1>
                <p className="text-slate-400 mt-1">Upload any Excel or CSV. We'll figure out the columns.</p>
            </div>

            {/* Step 1: Upload */}
            {step === 'upload' && (
                <div className="bg-slate-900 border-2 border-dashed border-slate-700 rounded-2xl p-12 text-center">
                    <Upload size={64} className="mx-auto text-slate-600 mb-4" />
                    <h3 className="text-xl font-semibold text-white mb-2">Drop your file here</h3>
                    <p className="text-slate-400 mb-6">Supported: Excel (.xlsx), CSV (.csv)</p>

                    <label className="cursor-pointer">
                        <input
                            type="file"
                            accept=".xlsx,.xls,.csv"
                            className="hidden"
                            onChange={handleFileChange}
                        />
                        <div className="bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-3 rounded-xl inline-block transition-colors">
                            Choose File
                        </div>
                    </label>

                    {loading && (
                        <div className="mt-6">
                            <div className="animate-spin h-8 w-8 border-4 border-indigo-500 border-t-transparent rounded-full mx-auto"></div>
                            <p className="text-slate-400 mt-2">Analyzing file structure...</p>
                        </div>
                    )}
                </div>
            )}

            {/* Step 2: Preview */}
            {step === 'preview' && preview && (
                <div className="space-y-6">
                    {/* Confidence Score */}
                    <div className={clsx(
                        "p-6 rounded-xl border-2",
                        preview.confidence >= 0.8 ? "bg-green-500/10 border-green-500/30" : "bg-yellow-500/10 border-yellow-500/30"
                    )}>
                        <div className="flex items-center gap-3">
                            {preview.confidence >= 0.8 ? (
                                <CheckCircle size={32} className="text-green-500" />
                            ) : (
                                <AlertCircle size={32} className="text-yellow-500" />
                            )}
                            <div>
                                <h3 className="text-lg font-semibold text-white">
                                    {(preview.confidence * 100).toFixed(0)}% Confidence
                                </h3>
                                <p className="text-sm text-slate-400">We detected {Object.keys(preview.detected_mapping).length} fields</p>
                            </div>
                        </div>
                    </div>

                    {/* Column Mapping */}
                    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                        <h3 className="font-semibold text-white mb-4">Detected Column Mapping</h3>
                        <div className="grid grid-cols-2 gap-4">
                            {Object.entries(preview.detected_mapping).map(([ourField, excelCol]) => (
                                <div key={ourField} className="flex items-center gap-3 text-sm">
                                    <span className="text-slate-500">{excelCol}</span>
                                    <ArrowRight size={16} className="text-indigo-400" />
                                    <span className="text-white font-medium">{ourField.replace('_', ' ')}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Warnings */}
                    {preview.warnings.length > 0 && (
                        <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-4">
                            <h4 className="text-yellow-500 font-medium mb-2">Warnings</h4>
                            <ul className="text-sm text-yellow-200 space-y-1">
                                {preview.warnings.map((w, i) => <li key={i}>• {w}</li>)}
                            </ul>
                        </div>
                    )}

                    {/* Sample Data */}
                    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                        <h3 className="font-semibold text-white mb-4">Preview ({preview.total_rows} total rows)</h3>
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead className="border-b border-slate-700">
                                    <tr>
                                        {Object.keys(preview.detected_mapping).map(field => (
                                            <th key={field} className="text-left p-2 text-slate-400 font-medium">{field}</th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody>
                                    {preview.sample_data.map((row, i) => (
                                        <tr key={i} className="border-b border-slate-800">
                                            {Object.keys(preview.detected_mapping).map(field => (
                                                <td key={field} className="p-2 text-white">{row[field] || '-'}</td>
                                            ))}
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-4">
                        <button
                            onClick={() => setStep('upload')}
                            className="flex-1 bg-slate-800 hover:bg-slate-700 text-white p-4 rounded-xl transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            onClick={handleImport}
                            disabled={loading}
                            className="flex-1 bg-green-600 hover:bg-green-500 text-white p-4 rounded-xl transition-colors disabled:opacity-50"
                        >
                            {loading ? 'Importing...' : `Import ${preview.total_rows} Students`}
                        </button>
                    </div>
                </div>
            )}

            {/* Step 3: Success */}
            {step === 'done' && (
                <div className="bg-green-500/10 border-2 border-green-500/30 rounded-2xl p-12 text-center">
                    <CheckCircle size={64} className="mx-auto text-green-500 mb-4" />
                    <h3 className="text-2xl font-semibold text-white mb-2">Import Complete!</h3>
                    <p className="text-slate-400 mb-6">All students have been added to your school.</p>
                    <button
                        onClick={() => window.location.href = '/admin'}
                        className="bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-3 rounded-xl transition-colors"
                    >
                        View Students
                    </button>
                </div>
            )}
        </div>
    );
};
