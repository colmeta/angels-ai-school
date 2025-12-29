/**
 * Dynamic PWA Manifest Manager
 * ============================
 * Allows the application to change its "Identity" based on the user role.
 * This enables the "5 PWAs" strategy where one codebase acts as 5 distinct operating systems.
 */

export type UserRole = 'teacher' | 'student' | 'parent' | 'admin' | 'director' | 'guest';

interface ManifestConfig {
    name: string;
    short_name: string;
    theme_color: string;
    start_url: string;
    icons: Array<{ src: string; sizes: string; type: string }>;
}

// Configs for each "OS"
const MANIFESTS: Record<UserRole | 'default', ManifestConfig> = {
    default: {
        name: 'Angels AI School',
        short_name: 'AngelsAI',
        theme_color: '#2563eb', // Blue
        start_url: '/',
        icons: [
            { src: '/pwa-192x192.png', sizes: '192x192', type: 'image/png' },
            { src: '/pwa-512x512.png', sizes: '512x512', type: 'image/png' }
        ]
    },
    teacher: {
        name: 'Angels Teacher OS',
        short_name: 'TeacherOS',
        theme_color: '#0ea5e9', // Sky Blue
        start_url: '/teacher',
        icons: [
            { src: '/icons/teacher-192.png', sizes: '192x192', type: 'image/png' },
            { src: '/icons/teacher-512.png', sizes: '512x512', type: 'image/png' }
        ]
    },
    student: {
        name: 'Angels Student Pulse',
        short_name: 'StudentPulse',
        theme_color: '#8b5cf6', // Violet
        start_url: '/student',
        icons: [
            { src: '/icons/student-192.png', sizes: '192x192', type: 'image/png' },
            { src: '/icons/student-512.png', sizes: '512x512', type: 'image/png' }
        ]
    },
    parent: {
        name: 'Angels Guardian Portal',
        short_name: 'Guardian',
        theme_color: '#10b981', // Emerald
        start_url: '/parent',
        icons: [
            { src: '/icons/parent-192.png', sizes: '192x192', type: 'image/png' },
            { src: '/icons/parent-512.png', sizes: '512x512', type: 'image/png' }
        ]
    },
    admin: {
        name: 'Angels Admin Core',
        short_name: 'AdminCore',
        theme_color: '#64748b', // Slate
        start_url: '/admin',
        icons: [
            { src: '/icons/admin-192.png', sizes: '192x192', type: 'image/png' },
            { src: '/icons/admin-512.png', sizes: '512x512', type: 'image/png' }
        ]
    },
    director: {
        name: 'Angels Director Suite',
        short_name: 'DirectorSuite',
        theme_color: '#eab308', // Gold
        start_url: '/director',
        icons: [
            { src: '/icons/director-192.png', sizes: '192x192', type: 'image/png' },
            { src: '/icons/director-512.png', sizes: '512x512', type: 'image/png' }
        ]
    },
    guest: { // Same as default
        name: 'Angels AI School',
        short_name: 'AngelsAI',
        theme_color: '#2563eb',
        start_url: '/',
        icons: [
            { src: '/pwa-192x192.png', sizes: '192x192', type: 'image/png' },
            { src: '/pwa-512x512.png', sizes: '512x512', type: 'image/png' }
        ]
    }
};

export const updateManifest = (role: UserRole) => {
    const config = MANIFESTS[role] || MANIFESTS.default;

    // 1. Create Manifest Blob
    const stringManifest = JSON.stringify(config);
    const blob = new Blob([stringManifest], { type: 'application/json' });
    const manifestURL = URL.createObjectURL(blob);

    // 2. Find existing manifest link
    let link = document.querySelector('link[rel="manifest"]');
    if (!link) {
        link = document.createElement('link');
        link.setAttribute('rel', 'manifest');
        document.head.appendChild(link);
    }

    // 3. Update href
    link.setAttribute('href', manifestURL);

    // 4. Update Theme Color Meta
    let metaTheme = document.querySelector('meta[name="theme-color"]');
    if (metaTheme) {
        metaTheme.setAttribute('content', config.theme_color);
    }

    console.log(`📱 PWA Identity switched to: ${config.name}`);
};

/**
 * Hook to auto-update manifest on mount based on stored role
 * (Call this in App.tsx or similar)
 */
export const useDynamicManifest = () => {
    // Determine initial role from localStorage or storage
    // using "try/catch" for safety
    try {
        const storedRole = localStorage.getItem('user_role') as UserRole;
        if (storedRole && MANIFESTS[storedRole]) {
            updateManifest(storedRole);
        } else {
            updateManifest('guest');
        }
    } catch (e) {
        console.error('Failed to update PWA manifest', e);
    }
};
