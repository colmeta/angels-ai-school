import { useState } from 'react';
import { Globe } from 'lucide-react';
import { getCurrentLanguage, setLanguage, type Language } from '../config/i18n';

export const LanguageSwitcher = () => {
    const [currentLang, setCurrentLang] = useState<Language>(getCurrentLanguage());

    const languages = [
        { code: 'en' as Language, name: 'English', flag: '🇬🇧' },
        { code: 'lg' as Language, name: 'Luganda', flag: '🇺🇬' },
        { code: 'sw' as Language, name: 'Swahili', flag: '🇹🇿' }
    ];

    const handleLanguageChange = (lang: Language) => {
        setCurrentLang(lang);
        setLanguage(lang);
    };

    return (
        <div className="relative group">
            <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800/50 hover:bg-slate-700/50 transition-colors border border-slate-700">
                <Globe size={18} />
                <span className="text-sm font-medium">
                    {languages.find(l => l.code === currentLang)?.flag} {languages.find(l => l.code === currentLang)?.name}
                </span>
            </button>

            {/* Dropdown */}
            <div className="absolute top-full right-0 mt-2 bg-slate-800 border border-slate-700 rounded-lg shadow-2xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50 min-w-[150px]">
                {languages.map((lang) => (
                    <button
                        key={lang.code}
                        onClick={() => handleLanguageChange(lang.code)}
                        className={`w-full flex items-center gap-3 px-4 py-3 hover:bg-slate-700 transition-colors text-left ${currentLang === lang.code ? 'bg-blue-600/20 text-blue-400' : 'text-white'
                            }`}
                    >
                        <span className="text-xl">{lang.flag}</span>
                        <span className="text-sm font-medium">{lang.name}</span>
                    </button>
                ))}
            </div>
        </div>
    );
};
