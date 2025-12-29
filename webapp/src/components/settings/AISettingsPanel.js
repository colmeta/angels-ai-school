import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { Settings, Cpu, Cloud, Zap, Check, AlertCircle, Info } from 'lucide-react';
import { getAIConfig, setAIMode, detectDeviceCapabilities, canRunMode } from '../../config/aiConfig';
export const AISettingsPanel = () => {
    const [currentMode, setCurrentMode] = useState('hybrid');
    const [capabilities, setCapabilities] = useState(detectDeviceCapabilities());
    const [activeConfig, setActiveConfig] = useState(getAIConfig());
    useEffect(() => {
        const config = getAIConfig();
        setCurrentMode(config.mode);
        setActiveConfig(config);
    }, []);
    const handleModeChange = (mode) => {
        if (!canRunMode(mode)) {
            alert(`Your device doesn't meet the minimum requirements for ${mode.toUpperCase()} mode`);
            return;
        }
        setAIMode(mode);
    };
    const modes = [
        {
            id: 'core',
            icon: Cpu,
            name: 'Core (Offline)',
            size: '200MB',
            ram: '>1GB RAM',
            badge: 'Power Users',
            badgeColor: 'blue',
            description: 'Full on-device AI, works 100% offline, highest accuracy',
            features: [
                'Complete offline functionality',
                'Full AI models on device',
                'Zero internet dependency',
                'Highest processing power',
                'Best for reliable internet'
            ],
            compatible: canRunMode('core')
        },
        {
            id: 'hybrid',
            icon: Cloud,
            name: 'Hybrid (Smart Sync)',
            size: '50MB',
            ram: '512MB RAM',
            badge: 'Recommended',
            badgeColor: 'green',
            description: 'On-device AI with cloud sync, perfect balance',
            features: [
                'On-device AI processing',
                'Cloud sync for results',
                'Cross-device access',
                'Works offline & online',
                'Best for most schools'
            ],
            compatible: canRunMode('hybrid'),
            recommended: true
        },
        {
            id: 'flash',
            icon: Zap,
            name: 'Flash (Cloud)',
            size: '30MB',
            ram: '256MB RAM',
            badge: 'Lightest',
            badgeColor: 'purple',
            description: 'Cloud-powered AI, fastest and lightest',
            features: [
                'Smallest app size',
                'Fastest responses',
                'Runs on any device',
                'Requires internet',
                'Optional cloud costs'
            ],
            compatible: canRunMode('flash')
        }
    ];
    return (_jsxs("div", { className: "max-w-6xl mx-auto p-6", children: [_jsxs("div", { className: "mb-8", children: [_jsxs("div", { className: "flex items-center gap-3 mb-4", children: [_jsx("div", { className: "w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center", children: _jsx(Settings, { className: "text-white", size: 24 }) }), _jsxs("div", { children: [_jsx("h1", { className: "text-3xl font-bold text-white", children: "AI Settings" }), _jsx("p", { className: "text-slate-400", children: "Choose the version that fits your device" })] })] }), _jsx("div", { className: "bg-slate-800/50 border border-slate-700 rounded-xl p-6", children: _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-3 gap-4", children: [_jsxs("div", { children: [_jsx("p", { className: "text-sm text-slate-400 mb-1", children: "Detected RAM" }), _jsxs("p", { className: "text-2xl font-bold text-white", children: [capabilities.ram, "MB"] })] }), _jsxs("div", { children: [_jsx("p", { className: "text-sm text-slate-400 mb-1", children: "Device Type" }), _jsx("p", { className: "text-2xl font-bold text-white", children: capabilities.isMobile ? 'Mobile' : 'Desktop' })] }), _jsxs("div", { children: [_jsx("p", { className: "text-sm text-slate-400 mb-1", children: "Recommended Mode" }), _jsx("p", { className: "text-2xl font-bold text-green-400 uppercase", children: capabilities.recommendedMode })] })] }) })] }), _jsx("div", { className: "grid md:grid-cols-3 gap-6 mb-8", children: modes.map((mode) => (_jsxs("div", { className: `relative bg-slate-800/50 border-2 rounded-2xl p-6 transition-all cursor-pointer ${currentMode === mode.id
                        ? 'border-green-500 shadow-2xl shadow-green-500/20'
                        : mode.compatible
                            ? 'border-slate-700 hover:border-slate-600'
                            : 'border-red-500/30 opacity-50 cursor-not-allowed'}`, onClick: () => mode.compatible && handleModeChange(mode.id), children: [mode.recommended && (_jsx("div", { className: "absolute -top-3 left-1/2 transform -translate-x-1/2 bg-gradient-to-r from-green-500 to-blue-500 text-white text-xs font-bold px-4 py-1 rounded-full", children: "\u2B50 BEST CHOICE" })), !mode.compatible && (_jsx("div", { className: "absolute -top-3 right-4 bg-red-500 text-white text-xs font-bold px-3 py-1 rounded-full", children: "Incompatible" })), currentMode === mode.id && (_jsxs("div", { className: "absolute -top-3 right-4 bg-green-500 text-white flex items-center gap-1 text-xs font-bold px-3 py-1 rounded-full", children: [_jsx(Check, { size: 14 }), "ACTIVE"] })), _jsxs("div", { className: `inline-flex items-center gap-2 bg-${mode.badgeColor}-500/20 border border-${mode.badgeColor}-500/50 rounded-full px-4 py-1 mb-4`, children: [_jsx(mode.icon, { size: 16, className: `text-${mode.badgeColor}-400` }), _jsx("span", { className: `text-${mode.badgeColor}-300 text-sm font-medium`, children: mode.badge })] }), _jsx("h3", { className: "text-xl font-bold text-white mb-2", children: mode.name }), _jsxs("div", { className: "flex gap-3 mb-3 text-sm text-slate-400", children: [_jsx("span", { children: mode.size }), _jsx("span", { children: "\u2022" }), _jsx("span", { children: mode.ram })] }), _jsx("p", { className: "text-slate-300 mb-4 text-sm", children: mode.description }), _jsx("ul", { className: "space-y-2 mb-6", children: mode.features.map((feature, idx) => (_jsxs("li", { className: "flex items-center gap-2 text-sm text-slate-400", children: [_jsx(Check, { size: 16, className: "text-green-400 flex-shrink-0" }), feature] }, idx))) }), mode.compatible && currentMode !== mode.id && (_jsxs("button", { className: `w-full py-3 rounded-xl font-bold transition-all ${mode.recommended
                                ? 'bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-500 hover:to-blue-500 text-white'
                                : 'bg-slate-700 hover:bg-slate-600 text-white'}`, children: ["Switch to ", mode.name.split(' ')[0]] }))] }, mode.id))) }), _jsxs("div", { className: "bg-slate-800/50 border border-slate-700 rounded-xl p-6", children: [_jsxs("h3", { className: "text-xl font-bold text-white mb-4 flex items-center gap-2", children: [_jsx(Info, { size: 20, className: "text-blue-400" }), "Current Configuration"] }), _jsxs("div", { className: "grid md:grid-cols-2 gap-6", children: [_jsxs("div", { children: [_jsx("h4", { className: "font-semibold text-white mb-3", children: "Features" }), _jsxs("ul", { className: "space-y-2 text-sm", children: [_jsxs("li", { className: "flex items-center gap-2", children: [activeConfig.features.offlineOnly ? (_jsx(Check, { className: "text-green-400", size: 16 })) : (_jsx(AlertCircle, { className: "text-yellow-400", size: 16 })), _jsxs("span", { className: "text-slate-300", children: ["Offline Mode: ", activeConfig.features.offlineOnly ? 'Always' : 'Optional'] })] }), _jsxs("li", { className: "flex items-center gap-2", children: [activeConfig.features.cloudSync ? (_jsx(Check, { className: "text-green-400", size: 16 })) : (_jsx(AlertCircle, { className: "text-slate-500", size: 16 })), _jsxs("span", { className: "text-slate-300", children: ["Cloud Sync: ", activeConfig.features.cloudSync ? 'Enabled' : 'Disabled'] })] }), _jsxs("li", { className: "flex items-center gap-2", children: [activeConfig.features.cloudFallback ? (_jsx(Check, { className: "text-green-400", size: 16 })) : (_jsx(AlertCircle, { className: "text-slate-500", size: 16 })), _jsxs("span", { className: "text-slate-300", children: ["Cloud Fallback: ", activeConfig.features.cloudFallback ? 'Available' : 'Disabled'] })] })] })] }), _jsxs("div", { children: [_jsx("h4", { className: "font-semibold text-white mb-3", children: "Performance Limits" }), _jsxs("ul", { className: "space-y-2 text-sm text-slate-300", children: [_jsxs("li", { children: ["\u2022 App Size: ~", activeConfig.limits.appSize, "MB"] }), _jsxs("li", { children: ["\u2022 Min RAM: ", activeConfig.limits.minRAM, "MB"] }), _jsxs("li", { children: ["\u2022 Max Concurrent: ", activeConfig.limits.maxConcurrent, " tasks"] }), _jsxs("li", { children: ["\u2022 Storage: ", activeConfig.storage.cloud ? 'Local + Cloud (R2)' : 'Local Only'] })] })] })] })] }), activeConfig.mode === 'flash' && (_jsx("div", { className: "mt-6 bg-yellow-500/10 border-2 border-yellow-500/50 rounded-xl p-6", children: _jsxs("div", { className: "flex items-start gap-3", children: [_jsx(AlertCircle, { className: "text-yellow-400 flex-shrink-0 mt-1", size: 24 }), _jsxs("div", { children: [_jsx("h4", { className: "font-bold text-yellow-300 mb-2", children: "Flash Mode Cost Notice" }), _jsx("p", { className: "text-yellow-200 text-sm mb-3", children: "Flash mode uses cloud AI which may incur costs if you exceed free tier limits:" }), _jsxs("ul", { className: "text-yellow-100 text-sm space-y-1", children: [_jsxs("li", { children: ["\u2022 Basic usage: ", _jsx("strong", { children: "FREE" }), " (up to 10,000 requests/month)"] }), _jsx("li", { children: "\u2022 Beyond free tier: ~$0.01 per request" }), _jsx("li", { children: "\u2022 You can disable cloud fallback anytime" }), _jsx("li", { children: "\u2022 All costs are transparent and tracked" })] })] })] }) }))] }));
};
