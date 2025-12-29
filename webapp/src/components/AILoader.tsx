// Minimal AILoader for Offline AI
import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain, Download, X, Loader2, Check } from 'lucide-react';
import { localAgent, AIStatus } from '../services/LocalAgentService';
import { t } from '../config/i18n';

export const AILoader = () => {
    const [status, setStatus] = useState<AIStatus>('idle');
    const [progress, setProgress] = useState(0);
    const [isMinimized, setIsMinimized] = useState(false);
    const [isVisible, setIsVisible] = useState(true);

    useEffect(() => {
        const unsubscribe = localAgent.subscribe((newStatus, newProgress) => {
            setStatus(newStatus);
            setProgress(newProgress);
            if (newStatus === 'loading') setIsVisible(true);
            if (newStatus === 'ready') setTimeout(() => setIsVisible(false), 5000);
        });
        return () => { unsubscribe(); };
    }, []);

    const handleStart = () => localAgent.loadModel();

    if (!isVisible && status === 'ready') return null;

    return (
        <AnimatePresence>
            {isVisible && (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 20 }}
                    className="fixed bottom-4 right-4 z-[50] flex flex-col items-end gap-2"
                >
                    {/* Collapsed State / Minimal Indicator */}
                    <div className="bg-slate-900 text-white p-3 rounded-full shadow-lg flex items-center gap-3 border border-slate-700 backdrop-blur-md bg-opacity-95">
                        <div className="flex items-center gap-2">
                            {status === 'loading' ? (
                                <Loader2 size={18} className="animate-spin text-blue-400" />
                            ) : status === 'ready' ? (
                                <Check size={18} className="text-emerald-400" />
                            ) : (
                                <Brain size={18} className="text-purple-400" />
                            )}

                            <div className="flex flex-col">
                                <span className="text-xs font-bold leading-none">
                                    {status === 'loading' ? t('ai.downloading') :
                                        status === 'ready' ? t('ai.ready') : t('ai.offlineCore')}
                                </span>
                                {status === 'idle' && (
                                    <span className="text-[10px] text-slate-400">{t('ai.freeDownload')} (200MB)</span>
                                )}
                            </div>
                        </div>

                        {status === 'idle' && (
                            <button
                                onClick={handleStart}
                                className="bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold px-3 py-1.5 rounded-full transition-colors flex items-center gap-1"
                            >
                                <Download size={12} /> {t('ai.download')}
                            </button>
                        )}

                        {status === 'loading' && (
                            <span className="text-xs font-mono text-blue-400">{Math.round(progress)}%</span>
                        )}

                        <button onClick={() => setIsVisible(false)} className="text-slate-500 hover:text-white ml-2">
                            <X size={14} />
                        </button>
                    </div>
                </motion.div>
            )}
        </AnimatePresence>
    );
};
