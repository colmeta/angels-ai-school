import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain, Cpu, CheckCircle2, AlertCircle, Download } from 'lucide-react';
import { localAgent, AIStatus } from '../services/LocalAgentService';

export const AILoader = () => {
    const [status, setStatus] = useState<AIStatus>('idle');
    const [progress, setProgress] = useState(0);
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        const unsubscribe = localAgent.subscribe((newStatus, newProgress) => {
            setStatus(newStatus);
            setProgress(newProgress);

            if (newStatus === 'loading') setIsVisible(true);
            if (newStatus === 'ready') {
                // Auto-hide after success
                setTimeout(() => setIsVisible(false), 3000);
            }
        });
        return unsubscribe;
    }, []);

    const handleStart = () => {
        localAgent.loadModel();
    };

    return (
        <AnimatePresence>
            {(isVisible || status === 'idle') && (
                <motion.div
                    initial={{ opacity: 0, y: 50 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    className="fixed bottom-6 right-6 z-[60] max-w-sm w-full"
                >
                    <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 p-5 overflow-hidden relative">
                        {/* Background Decoration */}
                        <div className="absolute -top-10 -right-10 w-32 h-32 bg-blue-50 rounded-full blur-3xl opacity-50" />

                        <div className="relative z-10">
                            <div className="flex items-start gap-4 mb-4">
                                <div className={`p-3 rounded-xl ${status === 'ready' ? 'bg-emerald-100 text-emerald-600' :
                                        status === 'error' ? 'bg-red-100 text-red-600' :
                                            'bg-blue-100 text-blue-600'
                                    }`}>
                                    {status === 'ready' ? <CheckCircle2 size={24} /> :
                                        status === 'error' ? <AlertCircle size={24} /> :
                                            status === 'loading' ? <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" /> :
                                                <Brain size={24} />}
                                </div>

                                <div className="flex-1">
                                    <h3 className="font-bold text-slate-900 leading-tight">
                                        {status === 'idle' ? 'Enable Zero-Cost AI Core?' :
                                            status === 'loading' ? 'Downloading AI Brain...' :
                                                status === 'ready' ? 'Edge AI Ready!' : 'Engine Error'}
                                    </h3>
                                    <p className="text-sm text-slate-500 mt-1">
                                        {status === 'idle' ? 'Unlock 100% offline intelligence & zero API fees (Requires ~200MB).' :
                                            status === 'loading' ? 'Fetching local model weights. This is only required once.' :
                                                status === 'ready' ? 'System upgraded. All actions are now processed locally.' :
                                                    'Failed to load. Please refresh your browser.'}
                                    </p>
                                </div>
                            </div>

                            {status === 'loading' && (
                                <div className="space-y-2">
                                    <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                                        <motion.div
                                            initial={{ width: 0 }}
                                            animate={{ width: `${progress}%` }}
                                            className="h-full bg-blue-600"
                                        />
                                    </div>
                                    <div className="flex justify-between text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                                        <span>Download Progress</span>
                                        <span>{Math.round(progress)}%</span>
                                    </div>
                                </div>
                            )}

                            {status === 'idle' && (
                                <button
                                    onClick={handleStart}
                                    className="w-full mt-2 bg-slate-900 text-white py-2.5 rounded-xl font-semibold hover:bg-slate-800 active:scale-95 transition-all flex items-center justify-center gap-2"
                                >
                                    <Download size={18} /> Initialize Edge AI
                                </button>
                            )}

                            {status === 'ready' && (
                                <div className="flex items-center gap-2 text-emerald-600 text-sm font-semibold justify-center py-1">
                                    <Cpu size={16} /> WebGPU Acceleration Active
                                </div>
                            )}
                        </div>
                    </div>
                </motion.div>
            )}
        </AnimatePresence>
    );
};
