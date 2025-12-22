import React, { useState, useEffect, useRef } from 'react';
import { Camera, Upload, Trash2, CheckCircle, Brain, RefreshCcw } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { localAgent } from '../services/LocalAgentService';
import { motion, AnimatePresence } from 'framer-motion';
import { useOfflineSync } from '../hooks/useOfflineSync';

export const SmartScan = () => {
    const { enqueueTask } = useOfflineSync();
    const navigate = useNavigate();
    const [image, setImage] = useState<string | null>(null);
    const [status, setStatus] = useState<'idle' | 'processing' | 'done'>('idle');
    const [ocrText, setOcrText] = useState('');
    const [progress, setProgress] = useState(0);
    const fileInputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        const unsubscribe = localAgent.subscribeOCR((text) => {
            setOcrText(text);
            setStatus('done');
        });

        const unsubscribeStatus = localAgent.subscribe((st, pr) => {
            if (st === 'loading') setStatus('processing');
            // Progress for OCR specifically comes from worker message
        });

        return () => {
            unsubscribe();
            unsubscribeStatus();
        };
    }, []);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (event) => {
            const dataUrl = event.target?.result as string;
            setImage(dataUrl);
            processImage(dataUrl);
        };
        reader.readAsDataURL(file);
    };

    const processImage = async (dataUrl: string) => {
        setStatus('processing');
        setProgress(0);
        await localAgent.processOCR(dataUrl);
    };

    const reset = () => {
        setImage(null);
        setOcrText('');
        setStatus('idle');
        setProgress(0);
    };

    return (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
            <div className="p-6 border-b border-slate-800 flex justify-between items-center">
                <div className="flex items-center gap-2 text-white font-bold">
                    <Camera className="text-blue-500" size={20} />
                    Smart Scan (OCR)
                </div>
                {image && (
                    <button onClick={reset} className="text-slate-500 hover:text-red-500 transition-colors">
                        <Trash2 size={18} />
                    </button>
                )}
            </div>

            <div className="p-6">
                {!image && (
                    <div
                        onClick={() => fileInputRef.current?.click()}
                        className="cursor-pointer border-2 border-dashed border-slate-800 hover:border-blue-500/50 hover:bg-blue-500/5 transition-all rounded-xl p-12 text-center group"
                    >
                        <Upload size={48} className="mx-auto text-slate-700 group-hover:text-blue-500 mb-4 transition-colors" />
                        <h3 className="text-white font-semibold mb-2">Upload or Take Photo</h3>
                        <p className="text-sm text-slate-500">Scan student lists, attendance sheets, or IDs locally.</p>
                        <input
                            type="file"
                            ref={fileInputRef}
                            onChange={handleFileChange}
                            accept="image/*"
                            className="hidden"
                        />
                    </div>
                )}

                {image && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="relative rounded-xl overflow-hidden bg-black border border-slate-800 aspect-video flex items-center justify-center">
                            <img src={image} alt="Source" className="max-h-full object-contain" />
                            {status === 'processing' && (
                                <div className="absolute inset-0 bg-black/60 backdrop-blur-sm flex flex-col items-center justify-center p-6 text-center">
                                    <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4" />
                                    <h4 className="text-white font-bold mb-1 italic">Reading Document...</h4>
                                    <p className="text-xs text-slate-400">On-device OCR engine active.</p>
                                </div>
                            )}
                        </div>

                        <div className="bg-slate-950 rounded-xl border border-slate-800 p-5 flex flex-col">
                            <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3 flex items-center justify-between">
                                <span>Extraction Results</span>
                                {status === 'done' && (
                                    <span className="flex items-center gap-1 text-emerald-500">
                                        <CheckCircle size={10} /> Local Complete
                                    </span>
                                )}
                            </div>

                            <div className="flex-1 overflow-auto max-h-[250px] font-mono text-sm text-slate-300 leading-relaxed whitespace-pre-wrap scrollbar-hide">
                                {ocrText || (
                                    <div className="h-full flex items-center justify-center text-slate-700 italic">
                                        Waiting for scan...
                                    </div>
                                )}
                            </div>

                            {status === 'done' && (
                                <button
                                    onClick={async () => {
                                        setStatus('processing');
                                        try {
                                            // Parse the OCR text into structure
                                            const result = await localAgent.parse(`Extract structured data from this OCR text: ${ocrText}`);

                                            // Enqueue / Execute
                                            enqueueTask('/agents/execute', {
                                                action: result.action,
                                                data: result.data,
                                                context: 'ocr_scan'
                                            }, 'POST');

                                            setStatus('done');
                                            alert("Data queued for processing!");
                                            reset();
                                        } catch (e) {
                                            console.error(e);
                                            setStatus('done');
                                        }
                                    }}
                                    className="w-full mt-4 bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-lg flex items-center justify-center gap-2 transition-all active:scale-95 shadow-lg shadow-blue-500/20"
                                >
                                    <Brain size={18} /> Send to AI Brain
                                </button>
                            )}
                        </div>
                    </div>
                )}
            </div>

            <div className="bg-slate-800/50 p-4 border-t border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-500/10 rounded-lg text-blue-500">
                        <RefreshCcw size={16} className={status === 'processing' ? 'animate-spin' : ''} />
                    </div>
                    <span className="text-xs font-medium text-slate-400">
                        {status === 'idle' ? 'Ready for next scan' :
                            status === 'processing' ? 'OCR engine running on hardware' :
                                'Extraction finished'}
                    </span>
                </div>
            </div>
        </div>
    );
};
