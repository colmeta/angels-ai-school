import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// Minimal AILoader for Offline AI
import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain, Download, X, Loader2, Check } from 'lucide-react';
import { localAgent } from '../services/LocalAgentService';
import { t } from '../config/i18n';
export const AILoader = () => {
    const [status, setStatus] = useState('idle');
    const [progress, setProgress] = useState(0);
    const [isMinimized, setIsMinimized] = useState(false);
    const [isVisible, setIsVisible] = useState(true);
    useEffect(() => {
        const unsubscribe = localAgent.subscribe((newStatus, newProgress) => {
            setStatus(newStatus);
            setProgress(newProgress);
            if (newStatus === 'loading')
                setIsVisible(true);
            if (newStatus === 'ready')
                setTimeout(() => setIsVisible(false), 5000);
        });
        return () => { unsubscribe(); };
    }, []);
    const handleStart = () => localAgent.loadModel();
    if (!isVisible && status === 'ready')
        return null;
    return (_jsx(AnimatePresence, { children: isVisible && (_jsx(motion.div, { initial: { opacity: 0, y: 20 }, animate: { opacity: 1, y: 0 }, exit: { opacity: 0, y: 20 }, className: "fixed bottom-4 right-4 z-[50] flex flex-col items-end gap-2", children: _jsxs("div", { className: "bg-slate-900 text-white p-3 rounded-full shadow-lg flex items-center gap-3 border border-slate-700 backdrop-blur-md bg-opacity-95", children: [_jsxs("div", { className: "flex items-center gap-2", children: [status === 'loading' ? (_jsx(Loader2, { size: 18, className: "animate-spin text-blue-400" })) : status === 'ready' ? (_jsx(Check, { size: 18, className: "text-emerald-400" })) : (_jsx(Brain, { size: 18, className: "text-purple-400" })), _jsxs("div", { className: "flex flex-col", children: [_jsx("span", { className: "text-xs font-bold leading-none", children: status === 'loading' ? t('ai.downloading') :
                                            status === 'ready' ? t('ai.ready') : t('ai.offlineCore') }), status === 'idle' && (_jsxs("span", { className: "text-[10px] text-slate-400", children: [t('ai.freeDownload'), " (200MB)"] }))] })] }), status === 'idle' && (_jsxs("button", { onClick: handleStart, className: "bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold px-3 py-1.5 rounded-full transition-colors flex items-center gap-1", children: [_jsx(Download, { size: 12 }), " ", t('ai.download')] })), status === 'loading' && (_jsxs("span", { className: "text-xs font-mono text-blue-400", children: [Math.round(progress), "%"] })), _jsx("button", { onClick: () => setIsVisible(false), className: "text-slate-500 hover:text-white ml-2", children: _jsx(X, { size: 14 }) })] }) })) }));
};
