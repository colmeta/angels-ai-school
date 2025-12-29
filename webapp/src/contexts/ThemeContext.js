import { jsx as _jsx } from "react/jsx-runtime";
import { useState, useEffect, createContext, useContext } from 'react';
const ThemeContext = createContext(undefined);
export const ThemeProvider = ({ children }) => {
    const [theme, setTheme] = useState(() => {
        // Check localStorage first
        const saved = localStorage.getItem('theme');
        if (saved === 'light' || saved === 'dark')
            return saved;
        // Check system preference
        if (window.matchMedia('(prefers-color-scheme: light)').matches) {
            return 'light';
        }
        return 'dark';
    });
    useEffect(() => {
        // Apply theme to document
        document.documentElement.classList.remove('light', 'dark');
        document.documentElement.classList.add(theme);
        localStorage.setItem('theme', theme);
    }, [theme]);
    const toggleTheme = () => {
        setTheme(prev => prev === 'dark' ? 'light' : 'dark');
    };
    return (_jsx(ThemeContext.Provider, { value: { theme, toggleTheme }, children: children }));
};
export const useTheme = () => {
    const context = useContext(ThemeContext);
    if (!context) {
        throw new Error('useTheme must be used within ThemeProvider');
    }
    return context;
};
// Theme toggle button component
import { Sun, Moon } from 'lucide-react';
export const ThemeToggle = () => {
    const { theme, toggleTheme } = useTheme();
    return (_jsx("button", { onClick: toggleTheme, className: "p-2 rounded-lg bg-slate-200 dark:bg-slate-800 hover:bg-slate-300 dark:hover:bg-slate-700 transition-colors", "aria-label": "Toggle theme", children: theme === 'dark' ? (_jsx(Sun, { size: 20, className: "text-yellow-500" })) : (_jsx(Moon, { size: 20, className: "text-slate-700" })) }));
};
