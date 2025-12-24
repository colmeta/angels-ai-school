/**
 * Multi-Language Support
 * Languages: English, Luganda, Swahili
 */

export type Language = 'en' | 'lg' | 'sw';

export interface Translation {
    en: string;
    lg: string;  // Luganda
    sw: string;  // Swahili
}

export const translations = {
    // Navigation
    nav: {
        features: { en: 'Features', lg: 'Ebisoboka', sw: 'Vipengele' },
        howItWorks: { en: 'How It Works', lg: 'Engeri Gye Kikola', sw: 'Jinsi Inavyofanya Kazi' },
        login: { en: 'Login', lg: 'Yingira', sw: 'Ingia' },
        getStarted: { en: 'Get Started Free', lg: 'Tandika Bwereere', sw: 'Anza Bure' }
    },

    // Hero Section
    hero: {
        free: { en: '100% Free Forever', lg: 'Bwereere Ennaku Zonna', sw: 'Bure Milele 100%' },
        noCard: { en: 'No Credit Card Required', lg: 'Teetaaga Kaadi ya Credit', sw: 'Hakuna Kadi ya Mkopo Inayohitajika' },
        transformEducation: { en: 'Transform Education', lg: 'Kyusa Ebyenjigiriza', sw: 'Badilisha Elimu' },
        aiOnPhone: { en: 'With AI That Lives On Your Phone', lg: 'Ne AI Ebeera Ku Ssimu Yo', sw: 'Na AI Inayoishi Kwenye Simu Yako' },
        description: {
            en: "The world's first school management platform with on-device AI that works offline, runs on 512MB RAM, and costs absolutely nothing.",
            lg: "Pulogulaamu y'okuddukanya esomero ey'omulembe eyimu era ya AI ekola mu ssimu nga tolina intaneti, ekola ne RAM ya 512MB, nga tebasasula.",
            sw: "Jukwaa la kwanza duniani la usimamizi wa shule lenye AI kwenye kifaa kinachofanya kazi nje ya mtandao, kinachofanya kazi kwenye RAM ya 512MB, na gharama ni sifuri kabisa."
        },
        startNow: { en: 'Start Using Now', lg: 'Tandika Kati', sw: 'Anza Kutumia Sasa' },
        watchDemo: { en: 'Watch Demo', lg: 'Laba Demo', sw: 'Tazama Onyesho' }
    },

    // Stats
    stats: {
        students: { en: '50K+ Students', lg: 'Abayizi 50K+', sw: 'Wanafunzi 50K+' },
        countries: { en: '12+ Countries', lg: 'Ensi 12+', sw: 'Nchi 12+' },
        rating: { en: '4.9/5 Rating', lg: 'Obubonero 4.9/5', sw: 'Ukadiriaji 4.9/5' },
        security: { en: 'Bank-Grade Security', lg: 'Obukuumi bwa Bbanka', sw: 'Usalama wa Kiwango cha Benki' }
    },

    // AI Modes
    modes: {
        core: {
            name: { en: 'Core (Offline)', lg: 'Core (Offline)', sw: 'Msingi (Nje ya Mtandao)' },
            badge: { en: 'Power Users', lg: 'Abakozesa Amaanyi', sw: 'Watumiaji Wenye Nguvu' },
            desc: {
                en: 'Full on-device AI, works 100% offline, highest accuracy',
                lg: 'AI y'enjawulo mu ssimu, ekola nga tolina intaneti, etuufu nnyo',
                sw: 'AI kamili kwenye kifaa, inafanya kazi 100% nje ya mtandao, usahihi wa juu zaidi'
            }
        },
        hybrid: {
            name: { en: 'Hybrid (Smart Sync)', lg: 'Hybrid (Smart Sync)', sw: 'Mseto (Usawazishaji Mahiri)' },
            badge: { en: 'Recommended', lg: 'Ekusuubizibwa', sw: 'Inayopendekezwa' },
            desc: {
                en: 'On-device AI with cloud sync, perfect balance',
                lg: 'AI mu ssimu ne ku cloud, ekozesa obulungi',
                sw: 'AI kwenye kifaa na usawazishaji wa wingu, usawa kamili'
            }
        },
        flash: {
            name: { en: 'Flash (Cloud)', lg: 'Flash (Cloud)', sw: 'Kasi (Wingu)' },
            badge: {
                en: 'Fastest', lg: 'Ey'amaanyi', sw: 'Haraka Zaidi' },
            desc: {
        en: 'Cloud-powered AI, fastest and lightest',
        lg: 'AI okuva mu cloud, ey'amaanyi era ey'epakasi',
        sw: 'AI inayoendeshwa na wingu, kasi zaidi na nyepesi'
            }
        }
    },

// Features
features: {
    studentMgmt: { en: 'Student Management', lg: 'Okuddukanya Abayizi', sw: 'Usimamizi wa Wanafunzi' },
    feeMgmt: { en: 'Fee Management', lg: 'Okuddukanya Ssente', sw: 'Usimamizi wa Ada' },
    reports: {
        en: 'Academic Reports', lg: 'Lipoota z'Amasomo', sw: 'Ripoti za Masomo' },
        parentComm: { en: 'Parent Communication', lg: 'Okwogera ne Bazadde', sw: 'Mawasiliano ya Wazazi' },
        library: { en: 'Library System', lg: 'Layiburali', sw: 'Mfumo wa Maktaba' },
        aiAssistant: { en: 'AI Assistant', lg: 'Omuyambi wa AI', sw: 'Msaidizi wa AI' }
    },

    // CTA
    cta: {
        ready: { en: 'Ready To Transform Your School?', lg: 'Omutegefu Okukyusa Essomero Lyo?', sw: 'Tayari Kubadilisha Shule Yako?' },
        join: { en: 'Join 50,000+ students already using Angels AI School', lg: 'Weegatte ku bayizi 50,000+ abakozesa Angels AI', sw: 'Jiunge na wanafunzi 50,000+ wanaotumia Angels AI' },
        noHidden: { en: 'No hidden fees', lg: 'Tewali bisale byekwese', sw: 'Hakuna ada zilizofichwa' }
    },

    // Settings
    settings: {
        aiSettings: { en: 'AI Settings', lg: 'Enteekateeka za AI', sw: 'Mipangilio ya AI' },
        chooseVersion: { en: 'Choose the version that fits your device', lg: 'Londako ekikola ku ssimu yo', sw: 'Chagua toleo linalofaa kifaa chako' },
        detectedRAM: { en: 'Detected RAM', lg: 'RAM Ezuuliddwa', sw: 'RAM Iliyogunduliwa' },
        deviceType: { en: 'Device Type', lg: 'Ekika kya Ssimu', sw: 'Aina ya Kifaa' },
        recommended: { en: 'Recommended Mode', lg: 'Enkola Ekusuubizibwa', sw: 'Hali Inayopendekezwa' },
        switchTo: { en: 'Switch to', lg: 'Kyusa okudda ku', sw: 'Badili kwenda' }
    }
};

// Get current language from localStorage or default to English
export function getCurrentLanguage(): Language {
    const stored = localStorage.getItem('language') as Language;
    return stored || 'en';
}

// Set language preference
export function setLanguage(lang: Language): void {
    localStorage.setItem('language', lang);
    window.location.reload();
}

// Translation helper
export function t(key: string): string {
    const lang = getCurrentLanguage();
    const keys = key.split('.');
    let value: any = translations;

    for (const k of keys) {
        value = value?.[k];
    }

    return value?.[lang] || value?.en || key;
}
