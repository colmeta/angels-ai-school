import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { ArrowRight, Brain, Check, Download, Globe2, Shield, Sparkles, Star, Zap, Cloud, WifiOff, Award, Users } from 'lucide-react';
import { t } from '../config/i18n';
export const LandingPage = () => {
    const [scrollY, setScrollY] = useState(0);
    useEffect(() => {
        const handleScroll = () => setScrollY(window.scrollY);
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);
    return (_jsxs("div", { className: "min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-purple-950 text-white overflow-hidden", children: [_jsxs("div", { className: "fixed inset-0 overflow-hidden pointer-events-none", children: [_jsx("div", { className: "absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-pulse" }), _jsx("div", { className: "absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-pulse delay-1000" }), _jsx("div", { className: "absolute top-1/2 left-1/2 w-96 h-96 bg-green-500/10 rounded-full blur-3xl animate-pulse delay-2000" })] }), _jsx("nav", { className: "fixed top-0 w-full z-50 backdrop-blur-xl bg-slate-950/80 border-b border-white/10", children: _jsxs("div", { className: "max-w-7xl mx-auto px-6 py-4 flex items-center justify-between", children: [_jsxs("div", { className: "flex items-center gap-3", children: [_jsx("div", { className: "w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center", children: _jsx(Sparkles, { className: "text-white", size: 24 }) }), _jsx("span", { className: "text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent", children: "Angels AI School" })] }), _jsxs("div", { className: "flex items-center gap-4", children: [_jsx("a", { href: "#features", className: "text-slate-300 hover:text-white transition-colors", children: t('nav.features') }), _jsx("a", { href: "#how-it-works", className: "text-slate-300 hover:text-white transition-colors", children: t('nav.howItWorks') }), _jsx("a", { href: "/login", className: "text-slate-300 hover:text-white transition-colors", children: t('nav.login') }), _jsx("a", { href: "/signup", className: "bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 px-6 py-2 rounded-full font-medium transition-all transform hover:scale-105", children: t('nav.getStarted') })] })] }) }), _jsx("section", { className: "relative pt-32 pb-20 px-6", children: _jsxs("div", { className: "max-w-7xl mx-auto text-center relative z-10", children: [_jsxs("div", { className: "inline-flex items-center gap-2 bg-green-500/20 border border-green-500/50 rounded-full px-6 py-2 mb-8 animate-pulse", children: [_jsx(Award, { size: 20, className: "text-green-400" }), _jsxs("span", { className: "text-green-300 font-medium", children: [t('hero.free'), " \u2022 ", t('hero.noCard')] })] }), _jsxs("h1", { className: "text-6xl md:text-8xl font-black mb-6 leading-tight", children: [_jsx("span", { className: "bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent", children: t('hero.transformEducation') }), _jsx("br", {}), _jsxs("span", { className: "text-white", children: [t('hero.aiOnPhone').split(' ')[0], " ", t('hero.aiOnPhone').split(' ').slice(1).join(' ')] })] }), _jsx("p", { className: "text-xl md:text-2xl text-slate-300 mb-12 max-w-3xl mx-auto leading-relaxed", children: t('hero.description') }), _jsxs("div", { className: "flex flex-col sm:flex-row gap-4 justify-center mb-16", children: [_jsxs("a", { href: "/signup", className: "group bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 px-10 py-5 rounded-2xl font-bold text-lg transition-all transform hover:scale-105 flex items-center justify-center gap-3 shadow-2xl shadow-blue-500/50", children: [t('hero.startNow'), _jsx(ArrowRight, { className: "group-hover:translate-x-1 transition-transform" })] }), _jsxs("a", { href: "#demo", className: "bg-slate-800/50 hover:bg-slate-700/50 border border-white/10 px-10 py-5 rounded-2xl font-bold text-lg transition-all flex items-center justify-center gap-3 backdrop-blur-xl", children: [_jsx(Download, { size: 24 }), t('hero.watchDemo')] })] }), _jsx("div", { className: "grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto", children: [
                                { icon: Users, label: '50K+ Students', color: 'blue' },
                                { icon: Globe2, label: '12+ Countries', color: 'green' },
                                { icon: Star, label: '4.9/5 Rating', color: 'yellow' },
                                { icon: Shield, label: 'Bank-Grade Security', color: 'purple' }
                            ].map((stat, i) => (_jsxs("div", { className: "bg-slate-800/30 backdrop-blur-xl border border-white/10 rounded-xl p-6 text-center", children: [_jsx(stat.icon, { size: 32, className: `mx-auto mb-2 text-${stat.color}-400` }), _jsx("p", { className: "text-lg font-bold", children: stat.label })] }, i))) })] }) }), _jsx("section", { className: "py-20 px-6 relative", children: _jsxs("div", { className: "max-w-7xl mx-auto relative z-10", children: [_jsxs("div", { className: "text-center mb-16", children: [_jsx("h2", { className: "text-5xl md:text-6xl font-black mb-6", children: _jsx("span", { className: "bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent", children: t('tech.title') }) }), _jsx("p", { className: "text-xl text-slate-300 max-w-3xl mx-auto", children: t('tech.subtitle') })] }), _jsx("div", { className: "grid md:grid-cols-3 gap-8", children: [
                                {
                                    icon: Brain,
                                    title: t('tech.onDevice.title'),
                                    desc: t('tech.onDevice.desc'),
                                    gradient: 'from-blue-500 to-cyan-500',
                                    features: [t('tech.onDevice.f1'), t('tech.onDevice.f2'), t('tech.onDevice.f3')]
                                },
                                {
                                    icon: WifiOff,
                                    title: t('tech.offline.title'),
                                    desc: t('tech.offline.desc'),
                                    gradient: 'from-purple-500 to-pink-500',
                                    features: [t('tech.offline.f1'), t('tech.offline.f2'), t('tech.offline.f3')]
                                },
                                {
                                    icon: Zap,
                                    title: t('tech.fast.title'),
                                    desc: t('tech.fast.desc'),
                                    gradient: 'from-yellow-500 to-orange-500',
                                    features: [t('tech.fast.f1'), t('tech.fast.f2'), t('tech.fast.f3')]
                                }
                            ].map((feature, i) => (_jsxs("div", { className: "group bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-xl border border-white/10 rounded-3xl p-8 hover:border-white/30 transition-all hover:scale-105 hover:shadow-2xl", children: [_jsx("div", { className: `w-16 h-16 bg-gradient-to-br ${feature.gradient} rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform`, children: _jsx(feature.icon, { size: 32, className: "text-white" }) }), _jsx("h3", { className: "text-2xl font-bold mb-4", children: feature.title }), _jsx("p", { className: "text-slate-300 mb-6 leading-relaxed", children: feature.desc }), _jsx("ul", { className: "space-y-2", children: feature.features.map((f, j) => (_jsxs("li", { className: "flex items-center gap-2 text-sm text-slate-400", children: [_jsx(Check, { size: 16, className: "text-green-400" }), f] }, j))) })] }, i))) })] }) }), _jsx("section", { id: "features", className: "py-20 px-6 bg-gradient-to-b from-slate-950/50 to-transparent", children: _jsxs("div", { className: "max-w-7xl mx-auto", children: [_jsx("h2", { className: "text-5xl font-black text-center mb-16", children: _jsx("span", { className: "bg-gradient-to-r from-green-400 to-blue-400 bg-clip-text text-transparent", children: t('features.title') }) }), _jsx("div", { className: "grid md:grid-cols-2 lg:grid-cols-3 gap-6", children: [
                                { icon: '👥', title: t('features.studentMgmt'), desc: t('features.studentMgmtDesc') },
                                { icon: '💰', title: t('features.feeMgmt'), desc: t('features.feeMgmtDesc') },
                                { icon: '📊', title: t('features.reports'), desc: t('features.reportsDesc') },
                                { icon: '📱', title: t('features.parentComm'), desc: t('features.parentCommDesc') },
                                { icon: '📚', title: t('features.library'), desc: t('features.libraryDesc') },
                                { icon: '🤖', title: t('features.aiAssistant'), desc: t('features.aiAssistantDesc') },
                                { icon: '📸', title: t('features.smartScan'), desc: t('features.smartScanDesc') },
                                { icon: '🔒', title: t('features.security'), desc: t('features.securityDesc') }
                            ].map((feature, i) => (_jsxs("div", { className: "bg-slate-800/30 backdrop-blur-xl border border-white/10 rounded-2xl p-6 hover:border-white/30 transition-all hover:scale-105", children: [_jsx("div", { className: "text-4xl mb-4", children: feature.icon }), _jsx("h3", { className: "text-xl font-bold mb-2", children: feature.title }), _jsx("p", { className: "text-slate-400 text-sm", children: feature.desc })] }, i))) })] }) }), _jsx("section", { className: "py-20 px-6", children: _jsxs("div", { className: "max-w-7xl mx-auto", children: [_jsx("h2", { className: "text-5xl font-black text-center mb-6", children: _jsx("span", { className: "bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent", children: t('settings.chooseVersion') }) }), _jsx("p", { className: "text-center text-slate-300 mb-16 text-xl", children: t('settings.chooseVersionDesc') }), _jsx("div", { className: "grid md:grid-cols-3 gap-8", children: [
                                {
                                    name: 'Core (Offline)',
                                    badge: 'Power Users',
                                    badgeColor: 'blue',
                                    size: '200MB',
                                    ram: '>1GB RAM',
                                    features: [
                                        'Full on-device AI',
                                        'Works 100% offline',
                                        'All features included',
                                        'Highest accuracy',
                                        'No internet needed'
                                    ],
                                    icon: WifiOff
                                },
                                {
                                    name: 'Hybrid (Smart Sync)',
                                    badge: 'Recommended',
                                    badgeColor: 'green',
                                    size: '50MB',
                                    ram: '512MB RAM',
                                    features: [
                                        'On-device AI',
                                        'Cloud sync for results',
                                        'Cross-device access',
                                        'Works offline',
                                        'Perfect for most schools'
                                    ],
                                    icon: Cloud,
                                    recommended: true
                                },
                                {
                                    name: 'Flash (Cloud)',
                                    badge: 'Fastest',
                                    badgeColor: 'purple',
                                    size: '30MB',
                                    ram: '256MB RAM',
                                    features: [
                                        'Cloud-powered AI',
                                        'Fastest responses',
                                        'Highest accuracy',
                                        'Lightest app',
                                        'Optional API costs*'
                                    ],
                                    icon: Zap
                                }
                            ].map((version, i) => (_jsxs("div", { className: `bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-xl border-2 rounded-3xl p-8 hover:scale-105 transition-all relative ${version.recommended ? 'border-green-500/50 shadow-2xl shadow-green-500/20' : 'border-white/10'}`, children: [version.recommended && (_jsxs("div", { className: "absolute -top-4 left-1/2 transform -translate-x-1/2 bg-gradient-to-r from-green-500 to-blue-500 text-white text-sm font-bold px-6 py-2 rounded-full", children: ["\u2B50 ", t('settings.bestChoice')] })), _jsxs("div", { className: `inline-flex items-center gap-2 bg-${version.badgeColor}-500/20 border border-${version.badgeColor}-500/50 rounded-full px-4 py-1 mb-6`, children: [_jsx(version.icon, { size: 16, className: `text-${version.badgeColor}-400` }), _jsx("span", { className: `text-${version.badgeColor}-300 text-sm font-medium`, children: version.badge })] }), _jsx("h3", { className: "text-3xl font-bold mb-2", children: version.name }), _jsxs("div", { className: "flex gap-3 mb-6 text-sm text-slate-400", children: [_jsx("span", { children: version.size }), _jsx("span", { children: "\u2022" }), _jsx("span", { children: version.ram })] }), _jsx("ul", { className: "space-y-3 mb-8", children: version.features.map((f, j) => (_jsxs("li", { className: "flex items-center gap-3 text-slate-300", children: [_jsx(Check, { size: 20, className: "text-green-400 flex-shrink-0" }), f] }, j))) }), _jsx("a", { href: "/signup", className: `block text-center py-4 rounded-xl font-bold transition-all ${version.recommended
                                            ? 'bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-500 hover:to-blue-500'
                                            : 'bg-slate-700 hover:bg-slate-600'}`, children: t('hero.getStarted') })] }, i))) }), _jsx("p", { className: "text-center text-slate-400 text-sm mt-8", children: "* Flash version: Free for basic usage. Optional cloud AI costs ~$0.01/request if you enable it (disabled by default)" })] }) }), _jsx("section", { className: "py-32 px-6", children: _jsx("div", { className: "max-w-4xl mx-auto text-center relative z-10", children: _jsxs("div", { className: "bg-gradient-to-r from-blue-600/20 via-purple-600/20 to-pink-600/20 backdrop-blur-xl border-2 border-white/20 rounded-3xl p-16", children: [_jsx("h2", { className: "text-5xl md:text-6xl font-black mb-6", children: t('cta.ready') }), _jsx("p", { className: "text-xl text-slate-300 mb-10", children: t('cta.join') }), _jsxs("a", { href: "/signup", className: "inline-flex items-center gap-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 px-12 py-6 rounded-2xl font-bold text-xl transition-all transform hover:scale-105 shadow-2xl shadow-blue-500/50", children: [t('nav.getStarted'), _jsx(ArrowRight, { size: 24 })] }), _jsx("p", { className: "text-slate-400 mt-6", children: t('cta.noHidden') })] }) }) }), _jsxs("footer", { className: "border-t border-white/10 py-12 px-6", children: [_jsxs("div", { className: "max-w-7xl mx-auto grid md:grid-cols-4 gap-8", children: [_jsxs("div", { children: [_jsxs("div", { className: "flex items-center gap-2 mb-4", children: [_jsx("div", { className: "w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center", children: _jsx(Sparkles, { size: 16, className: "text-white" }) }), _jsx("span", { className: "font-bold", children: "Angels AI School" })] }), _jsx("p", { className: "text-slate-400 text-sm", children: t('footer.tagline') })] }), _jsxs("div", { children: [_jsx("h4", { className: "font-bold mb-4", children: "Product" }), _jsxs("ul", { className: "space-y-2 text-slate-400 text-sm", children: [_jsx("li", { children: _jsx("a", { href: "#features", className: "hover:text-white", children: "Features" }) }), _jsx("li", { children: _jsx("a", { href: "#pricing", className: "hover:text-white", children: "Pricing" }) }), _jsx("li", { children: _jsx("a", { href: "/docs", className: "hover:text-white", children: "Documentation" }) })] })] }), _jsxs("div", { children: [_jsx("h4", { className: "font-bold mb-4", children: "Company" }), _jsxs("ul", { className: "space-y-2 text-slate-400 text-sm", children: [_jsx("li", { children: _jsx("a", { href: "/about", className: "hover:text-white", children: "About" }) }), _jsx("li", { children: _jsx("a", { href: "/blog", className: "hover:text-white", children: "Blog" }) }), _jsx("li", { children: _jsx("a", { href: "/contact", className: "hover:text-white", children: "Contact" }) })] })] }), _jsxs("div", { children: [_jsx("h4", { className: "font-bold mb-4", children: "Legal" }), _jsxs("ul", { className: "space-y-2 text-slate-400 text-sm", children: [_jsx("li", { children: _jsx("a", { href: "/privacy", className: "hover:text-white", children: "Privacy" }) }), _jsx("li", { children: _jsx("a", { href: "/terms", className: "hover:text-white", children: "Terms" }) }), _jsx("li", { children: _jsx("a", { href: "/security", className: "hover:text-white", children: "Security" }) })] })] })] }), _jsx("div", { className: "max-w-7xl mx-auto mt-12 pt-8 border-t border-white/10 text-center text-slate-400 text-sm", children: t('footer.copy') })] })] }));
};
