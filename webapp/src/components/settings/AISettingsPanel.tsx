import { useState, useEffect } from 'react';
import { Settings, Cpu, Cloud, Zap, Check, AlertCircle, Info } from 'lucide-react';
import { getAIConfig, setAIMode, detectDeviceCapabilities, canRunMode, type AIMode, type AIConfig, AI_CONFIGS } from '../../config/aiConfig';

export const AISettingsPanel = () => {
    const [currentMode, setCurrentMode] = useState<AIMode>('hybrid');
    const [capabilities, setCapabilities] = useState(detectDeviceCapabilities());
    const [activeConfig, setActiveConfig] = useState<AIConfig>(AI_CONFIGS.hybrid);

    useEffect(() => {
        const fetchConfig = async () => {
            const config = await getAIConfig();
            setCurrentMode(config.mode);
            setActiveConfig(config);
        };
        fetchConfig();
    }, []);

    const handleModeChange = (mode: AIMode) => {
        if (!canRunMode(mode)) {
            alert(`Your device doesn't meet the minimum requirements for ${mode.toUpperCase()} mode`);
            return;
        }
        setAIMode(mode);
    };

    const modes = [
        {
            id: 'core' as AIMode,
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
            id: 'hybrid' as AIMode,
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
            id: 'flash' as AIMode,
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

    return (
        <div className="max-w-6xl mx-auto p-6">
            {/* Header */}
            <div className="mb-8">
                <div className="flex items-center gap-3 mb-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                        <Settings className="text-white" size={24} />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold text-white">AI Settings</h1>
                        <p className="text-slate-400">Choose the version that fits your device</p>
                    </div>
                </div>

                {/* Device Info */}
                <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <p className="text-sm text-slate-400 mb-1">Detected RAM</p>
                            <p className="text-2xl font-bold text-white">{capabilities.ram}MB</p>
                        </div>
                        <div>
                            <p className="text-sm text-slate-400 mb-1">Device Type</p>
                            <p className="text-2xl font-bold text-white">{capabilities.isMobile ? 'Mobile' : 'Desktop'}</p>
                        </div>
                        <div>
                            <p className="text-sm text-slate-400 mb-1">Recommended Mode</p>
                            <p className="text-2xl font-bold text-green-400 uppercase">{capabilities.recommendedMode}</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Mode Selection */}
            <div className="grid md:grid-cols-3 gap-6 mb-8">
                {modes.map((mode) => (
                    <div
                        key={mode.id}
                        className={`relative bg-slate-800/50 border-2 rounded-2xl p-6 transition-all cursor-pointer ${currentMode === mode.id
                            ? 'border-green-500 shadow-2xl shadow-green-500/20'
                            : mode.compatible
                                ? 'border-slate-700 hover:border-slate-600'
                                : 'border-red-500/30 opacity-50 cursor-not-allowed'
                            }`}
                        onClick={() => mode.compatible && handleModeChange(mode.id)}
                    >
                        {mode.recommended && (
                            <div className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-gradient-to-r from-green-500 to-blue-500 text-white text-xs font-bold px-4 py-1 rounded-full">
                                ⭐ BEST CHOICE
                            </div>
                        )}

                        {!mode.compatible && (
                            <div className="absolute -top-3 right-4 bg-red-500 text-white text-xs font-bold px-3 py-1 rounded-full">
                                Incompatible
                            </div>
                        )}

                        {currentMode === mode.id && (
                            <div className="absolute -top-3 right-4 bg-green-500 text-white flex items-center gap-1 text-xs font-bold px-3 py-1 rounded-full">
                                <Check size={14} />
                                ACTIVE
                            </div>
                        )}

                        <div className={`inline-flex items-center gap-2 bg-${mode.badgeColor}-500/20 border border-${mode.badgeColor}-500/50 rounded-full px-4 py-1 mb-4`}>
                            <mode.icon size={16} className={`text-${mode.badgeColor}-400`} />
                            <span className={`text-${mode.badgeColor}-300 text-sm font-medium`}>{mode.badge}</span>
                        </div>

                        <h3 className="text-xl font-bold text-white mb-2">{mode.name}</h3>
                        <div className="flex gap-3 mb-3 text-sm text-slate-400">
                            <span>{mode.size}</span>
                            <span>•</span>
                            <span>{mode.ram}</span>
                        </div>
                        <p className="text-slate-300 mb-4 text-sm">{mode.description}</p>

                        <ul className="space-y-2 mb-6">
                            {mode.features.map((feature, idx) => (
                                <li key={idx} className="flex items-center gap-2 text-sm text-slate-400">
                                    <Check size={16} className="text-green-400 flex-shrink-0" />
                                    {feature}
                                </li>
                            ))}
                        </ul>

                        {mode.compatible && currentMode !== mode.id && (
                            <button
                                className={`w-full py-3 rounded-xl font-bold transition-all ${mode.recommended
                                    ? 'bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-500 hover:to-blue-500 text-white'
                                    : 'bg-slate-700 hover:bg-slate-600 text-white'
                                    }`}
                            >
                                Switch to {mode.name.split(' ')[0]}
                            </button>
                        )}
                    </div>
                ))}
            </div>

            {/* Current Configuration Details */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                    <Info size={20} className="text-blue-400" />
                    Current Configuration
                </h3>

                <div className="grid md:grid-cols-2 gap-6">
                    <div>
                        <h4 className="font-semibold text-white mb-3">Features</h4>
                        <ul className="space-y-2 text-sm">
                            <li className="flex items-center gap-2">
                                {activeConfig.features.offlineOnly ? (
                                    <Check className="text-green-400" size={16} />
                                ) : (
                                    <AlertCircle className="text-yellow-400" size={16} />
                                )}
                                <span className="text-slate-300">
                                    Offline Mode: {activeConfig.features.offlineOnly ? 'Always' : 'Optional'}
                                </span>
                            </li>
                            <li className="flex items-center gap-2">
                                {activeConfig.features.cloudSync ? (
                                    <Check className="text-green-400" size={16} />
                                ) : (
                                    <AlertCircle className="text-slate-500" size={16} />
                                )}
                                <span className="text-slate-300">
                                    Cloud Sync: {activeConfig.features.cloudSync ? 'Enabled' : 'Disabled'}
                                </span>
                            </li>
                            <li className="flex items-center gap-2">
                                {activeConfig.features.cloudFallback ? (
                                    <Check className="text-green-400" size={16} />
                                ) : (
                                    <AlertCircle className="text-slate-500" size={16} />
                                )}
                                <span className="text-slate-300">
                                    Cloud Fallback: {activeConfig.features.cloudFallback ? 'Available' : 'Disabled'}
                                </span>
                            </li>
                        </ul>
                    </div>

                    <div>
                        <h4 className="font-semibold text-white mb-3">Performance Limits</h4>
                        <ul className="space-y-2 text-sm text-slate-300">
                            <li>• App Size: ~{activeConfig.limits.appSize}MB</li>
                            <li>• Min RAM: {activeConfig.limits.minRAM}MB</li>
                            <li>• Max Concurrent: {activeConfig.limits.maxConcurrent} tasks</li>
                            <li>• Storage: {activeConfig.storage.cloud ? 'Local + Cloud (R2)' : 'Local Only'}</li>
                        </ul>
                    </div>
                </div>
            </div>

            {/* Cost Transparency */}
            {activeConfig.mode === 'flash' && (
                <div className="mt-6 bg-yellow-500/10 border-2 border-yellow-500/50 rounded-xl p-6">
                    <div className="flex items-start gap-3">
                        <AlertCircle className="text-yellow-400 flex-shrink-0 mt-1" size={24} />
                        <div>
                            <h4 className="font-bold text-yellow-300 mb-2">Flash Mode Cost Notice</h4>
                            <p className="text-yellow-200 text-sm mb-3">
                                Flash mode uses cloud AI which may incur costs if you exceed free tier limits:
                            </p>
                            <ul className="text-yellow-100 text-sm space-y-1">
                                <li>• Basic usage: <strong>FREE</strong> (up to 10,000 requests/month)</li>
                                <li>• Beyond free tier: ~$0.01 per request</li>
                                <li>• You can disable cloud fallback anytime</li>
                                <li>• All costs are transparent and tracked</li>
                            </ul>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};
