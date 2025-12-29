import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useState } from 'react';
import { MessageCircle, X, Send, Minimize2 } from 'lucide-react';
import clsx from 'clsx';
export const ReceptionistWidget = ({ schoolId, position = 'bottom-right', primaryColor = '#2563eb' }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [isMinimized, setIsMinimized] = useState(false);
    const [messages, setMessages] = useState([
        {
            role: 'bot',
            content: 'Hello! I\'m the school AI receptionist. How can I help you today?',
            timestamp: new Date()
        }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [suggestions, setSuggestions] = useState([
        'School fees',
        'Admissions',
        'Contact us'
    ]);
    const sendMessage = async () => {
        if (!input.trim())
            return;
        const userMessage = {
            role: 'user',
            content: input,
            timestamp: new Date()
        };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setLoading(true);
        try {
            const response = await fetch(`/api/receptionist/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: input,
                    school_id: schoolId
                })
            });
            const data = await response.json();
            const botMessage = {
                role: 'bot',
                content: data.reply,
                timestamp: new Date()
            };
            setMessages(prev => [...prev, botMessage]);
            setSuggestions(data.suggestions || []);
        }
        catch (error) {
            const errorMessage = {
                role: 'bot',
                content: 'Sorry, I\'m having trouble connecting. Please try again.',
                timestamp: new Date()
            };
            setMessages(prev => [...prev, errorMessage]);
        }
        finally {
            setLoading(false);
        }
    };
    const handleSuggestionClick = (suggestion) => {
        setInput(suggestion);
        sendMessage();
    };
    if (!isOpen) {
        return (_jsx("button", { onClick: () => setIsOpen(true), className: clsx("fixed z-50 w-16 h-16 rounded-full shadow-2xl flex items-center justify-center transition-transform hover:scale-110", position === 'bottom-right' ? 'bottom-6 right-6' : 'bottom-6 left-6'), style: { backgroundColor: primaryColor }, children: _jsx(MessageCircle, { size: 28, className: "text-white" }) }));
    }
    return (_jsxs("div", { className: clsx("fixed z-50 flex flex-col bg-white dark:bg-slate-800 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-700 transition-all", position === 'bottom-right' ? 'bottom-6 right-6' : 'bottom-6 left-6', isMinimized ? 'w-80 h-16' : 'w-96 h-[600px]'), children: [_jsxs("div", { className: "flex items-center justify-between p-4 border-b border-slate-200 dark:border-slate-700 rounded-t-2xl", style: { backgroundColor: primaryColor }, children: [_jsxs("div", { className: "flex items-center gap-3", children: [_jsx("div", { className: "w-10 h-10 rounded-full bg-white/20 flex items-center justify-center", children: _jsx(MessageCircle, { size: 20, className: "text-white" }) }), _jsxs("div", { children: [_jsx("h3", { className: "font-semibold text-white", children: "AI Receptionist" }), _jsx("p", { className: "text-xs text-white/80", children: "Online 24/7" })] })] }), _jsxs("div", { className: "flex items-center gap-2", children: [_jsx("button", { onClick: () => setIsMinimized(!isMinimized), className: "text-white hover:bg-white/20 p-2 rounded-lg transition-colors", children: _jsx(Minimize2, { size: 18 }) }), _jsx("button", { onClick: () => setIsOpen(false), className: "text-white hover:bg-white/20 p-2 rounded-lg transition-colors", children: _jsx(X, { size: 18 }) })] })] }), !isMinimized && (_jsxs(_Fragment, { children: [_jsxs("div", { className: "flex-1 overflow-y-auto p-4 space-y-4", children: [messages.map((msg, i) => (_jsx("div", { className: clsx("flex", msg.role === 'user' ? 'justify-end' : 'justify-start'), children: _jsx("div", { className: clsx("max-w-[80%] p-3 rounded-2xl", msg.role === 'user'
                                        ? 'bg-blue-600 text-white rounded-br-none'
                                        : 'bg-slate-100 dark:bg-slate-700 text-slate-900 dark:text-white rounded-bl-none'), children: _jsx("p", { className: "text-sm", children: msg.content }) }) }, i))), loading && (_jsx("div", { className: "flex justify-start", children: _jsx("div", { className: "bg-slate-100 dark:bg-slate-700 p-3 rounded-2xl rounded-bl-none", children: _jsxs("div", { className: "flex gap-1", children: [_jsx("div", { className: "w-2 h-2 bg-slate-400 rounded-full animate-bounce", style: { animationDelay: '0ms' } }), _jsx("div", { className: "w-2 h-2 bg-slate-400 rounded-full animate-bounce", style: { animationDelay: '150ms' } }), _jsx("div", { className: "w-2 h-2 bg-slate-400 rounded-full animate-bounce", style: { animationDelay: '300ms' } })] }) }) }))] }), suggestions.length > 0 && (_jsx("div", { className: "px-4 pb-2 flex flex-wrap gap-2", children: suggestions.map((suggestion, i) => (_jsx("button", { onClick: () => handleSuggestionClick(suggestion), className: "text-xs bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-300 px-3 py-1.5 rounded-full transition-colors", children: suggestion }, i))) })), _jsx("div", { className: "p-4 border-t border-slate-200 dark:border-slate-700", children: _jsxs("div", { className: "flex gap-2", children: [_jsx("input", { type: "text", value: input, onChange: (e) => setInput(e.target.value), onKeyPress: (e) => e.key === 'Enter' && sendMessage(), placeholder: "Type your message...", className: "flex-1 bg-slate-100 dark:bg-slate-700 border-0 rounded-xl px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" }), _jsx("button", { onClick: sendMessage, disabled: loading || !input.trim(), className: "bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white p-2 rounded-xl transition-colors", style: { backgroundColor: primaryColor }, children: _jsx(Send, { size: 18 }) })] }) })] }))] }));
};
// Embeddable snippet generator
export const generateEmbedCode = (schoolId, primaryColor) => {
    return `
<!-- Angels AI 24/7 Receptionist -->
<script>
  window.AngelsAIConfig = {
    schoolId: "${schoolId}",
    primaryColor: "${primaryColor || '#2563eb'}"
  };
</script>
<script src="https://cdn.angels-ai.com/widget.js" defer></script>
    `.trim();
};
