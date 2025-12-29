import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * Voice Input Component
 * Press & hold to record voice commands
 */
import { useState } from 'react';
import { useVoiceCommands } from '@/hooks/useVoiceCommands';
export function VoiceInput({ schoolId, onResult, onError, disabled }) {
    const [feedback, setFeedback] = useState('');
    const [feedbackType, setFeedbackType] = useState('info');
    const { isSupported, isListening, isProcessing, transcript, startListening, stopListening, } = useVoiceCommands({
        schoolId,
        onResult: (result) => {
            if (result.success) {
                setFeedback(`✅ ${result.command || 'Command executed successfully'}`);
                setFeedbackType('success');
            }
            else {
                setFeedback(`❌ ${result.error || 'Command failed'}`);
                setFeedbackType('error');
            }
            onResult?.(result);
            // Clear feedback after 5 seconds
            setTimeout(() => setFeedback(''), 5000);
        },
        onError: (error) => {
            setFeedback(`❌ ${error}`);
            setFeedbackType('error');
            onError?.(error);
            setTimeout(() => setFeedback(''), 5000);
        },
    });
    if (!isSupported) {
        return (_jsxs("div", { className: "bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-sm text-yellow-800", children: [_jsx("p", { className: "font-medium", children: "\u26A0\uFE0F Voice commands not supported" }), _jsx("p", { className: "mt-1", children: "Your browser doesn't support voice recognition. Please use Chrome, Safari, or Edge." })] }));
    }
    return (_jsxs("div", { className: "space-y-3", children: [_jsx("div", { className: "flex items-center justify-center", children: _jsx("button", { type: "button", onMouseDown: startListening, onMouseUp: stopListening, onTouchStart: startListening, onTouchEnd: stopListening, disabled: disabled || isProcessing, className: `
            relative w-20 h-20 rounded-full flex items-center justify-center
            transition-all duration-200 shadow-lg
            ${isListening
                        ? 'bg-red-500 scale-110 animate-pulse'
                        : 'bg-blue-500 hover:bg-blue-600 active:scale-95'}
            ${disabled || isProcessing ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
          `, children: isProcessing ? (_jsxs("svg", { className: "w-8 h-8 text-white animate-spin", fill: "none", viewBox: "0 0 24 24", children: [_jsx("circle", { className: "opacity-25", cx: "12", cy: "12", r: "10", stroke: "currentColor", strokeWidth: "4" }), _jsx("path", { className: "opacity-75", fill: "currentColor", d: "M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" })] })) : (_jsxs("svg", { className: "w-8 h-8 text-white", fill: "currentColor", viewBox: "0 0 24 24", children: [_jsx("path", { d: "M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" }), _jsx("path", { d: "M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" })] })) }) }), _jsx("div", { className: "text-center", children: _jsx("p", { className: "text-sm font-medium text-gray-700", children: isListening ? (_jsx("span", { className: "text-red-600", children: "\uD83C\uDFA4 Listening... Release to send" })) : isProcessing ? (_jsx("span", { className: "text-blue-600", children: "\u23F3 Processing command..." })) : (_jsx("span", { className: "text-gray-600", children: "Press & hold to speak" })) }) }), transcript && (_jsxs("div", { className: "bg-gray-50 border border-gray-200 rounded-lg p-3 min-h-[60px]", children: [_jsx("p", { className: "text-sm text-gray-600 mb-1", children: "You said:" }), _jsx("p", { className: "text-base font-medium text-gray-900", children: transcript })] })), feedback && (_jsx("div", { className: `
            border rounded-lg p-3
            ${feedbackType === 'success' ? 'bg-green-50 border-green-200 text-green-800' : ''}
            ${feedbackType === 'error' ? 'bg-red-50 border-red-200 text-red-800' : ''}
            ${feedbackType === 'info' ? 'bg-blue-50 border-blue-200 text-blue-800' : ''}
          `, children: _jsx("p", { className: "text-sm font-medium", children: feedback }) })), _jsxs("div", { className: "bg-blue-50 border border-blue-200 rounded-lg p-3", children: [_jsx("p", { className: "text-sm font-medium text-blue-900 mb-2", children: "\uD83D\uDCDD Example Commands:" }), _jsxs("ul", { className: "text-xs text-blue-800 space-y-1", children: [_jsx("li", { children: "\u2022 \"Mark John as present\"" }), _jsx("li", { children: "\u2022 \"Mark all Class 5A as present\"" }), _jsx("li", { children: "\u2022 \"Record 85 marks for Mary in Math\"" }), _jsx("li", { children: "\u2022 \"Send message to all parents: School closes early\"" })] })] })] }));
}
