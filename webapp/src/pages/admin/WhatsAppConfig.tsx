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
    const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);

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

    return (
        <div className="p-6 md:p-8 max-w-3xl mx-auto">
            <div className="mb-8">
                <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                    <MessageSquare size={28} className="text-green-400" />
                    WhatsApp Configuration
                </h1>
                <p className="text-slate-400 mt-1">Connect your Twilio WhatsApp Business Account</p>
            </div>

            {/* Twilio Credentials */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
                <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                        Twilio Account SID
                    </label>
                    <input
                        type="text"
                        value={config.accountSid}
                        onChange={(e) => setConfig({ ...config, accountSid: e.target.value })}
                        placeholder="AC..."
                        className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                        Auth Token
                    </label>
                    <input
                        type="password"
                        value={config.authToken}
                        onChange={(e) => setConfig({ ...config, authToken: e.target.value })}
                        placeholder="••••••••"
                        className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                        WhatsApp Number
                    </label>
                    <input
                        type="text"
                        value={config.fromNumber}
                        onChange={(e) => setConfig({ ...config, fromNumber: e.target.value })}
                        placeholder="+1 415 523 8886"
                        className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                    />
                    <p className="text-xs text-slate-500 mt-1">Your Twilio WhatsApp sandbox or approved number</p>
                </div>

                <button
                    onClick={handleSave}
                    className="w-full bg-green-600 hover:bg-green-500 text-white px-6 py-3 rounded-xl transition-colors font-medium"
                >
                    Save Configuration
                </button>
            </div>

            {/* Test Section */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 mt-6">
                <h3 className="font-semibold text-white mb-4">Test Connection</h3>

                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                            Test Phone Number
                        </label>
                        <input
                            type="tel"
                            value={testPhone}
                            onChange={(e) => setTestPhone(e.target.value)}
                            placeholder="+256 700 000 000"
                            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                        />
                    </div>

                    <button
                        onClick={handleTest}
                        disabled={!testPhone || testing}
                        className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white px-6 py-3 rounded-xl transition-colors font-medium flex items-center justify-center gap-2"
                    >
                        {testing ? (
                            <>
                                <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                                Sending...
                            </>
                        ) : (
                            <>
                                <Send size={18} />
                                Send Test Message
                            </>
                        )}
                    </button>

                    {testResult && (
                        <div className={clsx(
                            "p-4 rounded-lg flex items-start gap-3",
                            testResult.success ? "bg-green-500/10 border border-green-500/30" : "bg-red-500/10 border border-red-500/30"
                        )}>
                            {testResult.success ? (
                                <CheckCircle size={20} className="text-green-500 flex-shrink-0 mt-0.5" />
                            ) : (
                                <AlertCircle size={20} className="text-red-500 flex-shrink-0 mt-0.5" />
                            )}
                            <div>
                                <p className={clsx("text-sm font-medium", testResult.success ? "text-green-400" : "text-red-400")}>
                                    {testResult.success ? 'Success!' : 'Failed'}
                                </p>
                                <p className="text-sm text-slate-300 mt-1">{testResult.message}</p>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Setup Guide */}
            <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-6 mt-6">
                <h3 className="font-semibold text-blue-400 mb-3">Quick Setup Guide</h3>
                <ol className="text-sm text-slate-300 space-y-2 list-decimal list-inside">
                    <li>Create a <a href="https://www.twilio.com/try-twilio" target="_blank" rel="noopener noreferrer" className="text-blue-400 underline">Twilio account</a></li>
                    <li>Get your Account SID and Auth Token from the <a href="https://console.twilio.com" target="_blank" rel="noopener noreferrer" className="text-blue-400 underline">Twilio Console</a></li>
                    <li>Set up <a href="https://www.twilio.com/docs/whatsapp/sandbox" target="_blank" rel="noopener noreferrer" className="text-blue-400 underline">WhatsApp Sandbox</a> (for testing)</li>
                    <li>Enter credentials above and test</li>
                    <li>For production: Apply for <a href="https://www.twilio.com/whatsapp/request-access" target="_blank" rel="noopener noreferrer" className="text-blue-400 underline">WhatsApp Business approval</a></li>
                </ol>
            </div>
        </div>
    );
};
