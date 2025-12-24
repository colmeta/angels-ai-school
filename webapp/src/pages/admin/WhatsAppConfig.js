import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
/**
 * Admin Configuration UI for WhatsApp Business Account
 * Allows directors to set up Twilio credentials and test messages
 */
import { useState } from 'react';
import { MessageSquare, CheckCircle, AlertCircle, Send } from 'lucide-react';
import clsx from 'clsx';
export const WhatsAppConfig = () => {
    const [config, setConfig] = useState({
        accountSid: '',
        authToken: '',
        fromNumber: ''
    });
    const [testPhone, setTestPhone] = useState('');
    const [testing, setTesting] = useState(false);
    const [testResult, setTestResult] = useState(null);
    const handleSave = async () => {
        // TODO: API call to save config
        alert('Configuration saved (backend integration pending)');
    };
    const handleTest = async () => {
        setTesting(true);
        setTestResult(null);
        // Mock test (replace with actual API call)
        setTimeout(() => {
            setTestResult({
                success: true,
                message: `Test message sent to ${testPhone}`
            });
            setTesting(false);
        }, 2000);
    };
    return (_jsxs("div", { className: "p-6 md:p-8 max-w-3xl mx-auto", children: [_jsxs("div", { className: "mb-8", children: [_jsxs("h1", { className: "text-2xl font-bold text-white flex items-center gap-2", children: [_jsx(MessageSquare, { size: 28, className: "text-green-400" }), "WhatsApp Configuration"] }), _jsx("p", { className: "text-slate-400 mt-1", children: "Connect your Twilio WhatsApp Business Account" })] }), _jsxs("div", { className: "bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4", children: [_jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-slate-300 mb-2", children: "Twilio Account SID" }), _jsx("input", { type: "text", value: config.accountSid, onChange: (e) => setConfig({ ...config, accountSid: e.target.value }), placeholder: "AC...", className: "w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-green-500" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-slate-300 mb-2", children: "Auth Token" }), _jsx("input", { type: "password", value: config.authToken, onChange: (e) => setConfig({ ...config, authToken: e.target.value }), placeholder: "\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022", className: "w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-green-500" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-slate-300 mb-2", children: "WhatsApp Number" }), _jsx("input", { type: "text", value: config.fromNumber, onChange: (e) => setConfig({ ...config, fromNumber: e.target.value }), placeholder: "+1 415 523 8886", className: "w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-green-500" }), _jsx("p", { className: "text-xs text-slate-500 mt-1", children: "Your Twilio WhatsApp sandbox or approved number" })] }), _jsx("button", { onClick: handleSave, className: "w-full bg-green-600 hover:bg-green-500 text-white px-6 py-3 rounded-xl transition-colors font-medium", children: "Save Configuration" })] }), _jsxs("div", { className: "bg-slate-900 border border-slate-800 rounded-xl p-6 mt-6", children: [_jsx("h3", { className: "font-semibold text-white mb-4", children: "Test Connection" }), _jsxs("div", { className: "space-y-4", children: [_jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-slate-300 mb-2", children: "Test Phone Number" }), _jsx("input", { type: "tel", value: testPhone, onChange: (e) => setTestPhone(e.target.value), placeholder: "+256 700 000 000", className: "w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-green-500" })] }), _jsx("button", { onClick: handleTest, disabled: !testPhone || testing, className: "w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white px-6 py-3 rounded-xl transition-colors font-medium flex items-center justify-center gap-2", children: testing ? (_jsxs(_Fragment, { children: [_jsx("div", { className: "animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full" }), "Sending..."] })) : (_jsxs(_Fragment, { children: [_jsx(Send, { size: 18 }), "Send Test Message"] })) }), testResult && (_jsxs("div", { className: clsx("p-4 rounded-lg flex items-start gap-3", testResult.success ? "bg-green-500/10 border border-green-500/30" : "bg-red-500/10 border border-red-500/30"), children: [testResult.success ? (_jsx(CheckCircle, { size: 20, className: "text-green-500 flex-shrink-0 mt-0.5" })) : (_jsx(AlertCircle, { size: 20, className: "text-red-500 flex-shrink-0 mt-0.5" })), _jsxs("div", { children: [_jsx("p", { className: clsx("text-sm font-medium", testResult.success ? "text-green-400" : "text-red-400"), children: testResult.success ? 'Success!' : 'Failed' }), _jsx("p", { className: "text-sm text-slate-300 mt-1", children: testResult.message })] })] }))] })] }), _jsxs("div", { className: "bg-blue-500/10 border border-blue-500/30 rounded-xl p-6 mt-6", children: [_jsx("h3", { className: "font-semibold text-blue-400 mb-3", children: "Quick Setup Guide" }), _jsxs("ol", { className: "text-sm text-slate-300 space-y-2 list-decimal list-inside", children: [_jsxs("li", { children: ["Create a ", _jsx("a", { href: "https://www.twilio.com/try-twilio", target: "_blank", rel: "noopener noreferrer", className: "text-blue-400 underline", children: "Twilio account" })] }), _jsxs("li", { children: ["Get your Account SID and Auth Token from the ", _jsx("a", { href: "https://console.twilio.com", target: "_blank", rel: "noopener noreferrer", className: "text-blue-400 underline", children: "Twilio Console" })] }), _jsxs("li", { children: ["Set up ", _jsx("a", { href: "https://www.twilio.com/docs/whatsapp/sandbox", target: "_blank", rel: "noopener noreferrer", className: "text-blue-400 underline", children: "WhatsApp Sandbox" }), " (for testing)"] }), _jsx("li", { children: "Enter credentials above and test" }), _jsxs("li", { children: ["For production: Apply for ", _jsx("a", { href: "https://www.twilio.com/whatsapp/request-access", target: "_blank", rel: "noopener noreferrer", className: "text-blue-400 underline", children: "WhatsApp Business approval" })] })] })] })] }));
};
