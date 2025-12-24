import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { Globe } from 'lucide-react';
import { getCurrentLanguage, setLanguage } from '../config/i18n';
export const LanguageSwitcher = () => {
    const [currentLang, setCurrentLang] = useState(getCurrentLanguage());
    const languages = [
        { code: 'en', name: 'English', flag: '🇬🇧' },
        { code: 'lg', name: 'Luganda', flag: '🇺🇬' },
        { code: 'sw', name: 'Swahili', flag: '🇹🇿' }
    ];
    const handleLanguageChange = (lang) => {
        setCurrentLang(lang);
        setLanguage(lang);
    };
    return (_jsxs("div", { className: "relative group", children: [_jsxs("button", { className: "flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800/50 hover:bg-slate-700/50 transition-colors border border-slate-700", children: [_jsx(Globe, { size: 18 }), _jsxs("span", { className: "text-sm font-medium", children: [languages.find(l => l.code === currentLang)?.flag, " ", languages.find(l => l.code === currentLang)?.name] })] }), _jsx("div", { className: "absolute top-full right-0 mt-2 bg-slate-800 border border-slate-700 rounded-lg shadow-2xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50 min-w-[150px]", children: languages.map((lang) => (_jsxs("button", { onClick: () => handleLanguageChange(lang.code), className: `w-full flex items-center gap-3 px-4 py-3 hover:bg-slate-700 transition-colors text-left ${currentLang === lang.code ? 'bg-blue-600/20 text-blue-400' : 'text-white'}`, children: [_jsx("span", { className: "text-xl", children: lang.flag }), _jsx("span", { className: "text-sm font-medium", children: lang.name })] }, lang.code))) })] }));
};
