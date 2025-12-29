import { Fragment as _Fragment, jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { Menu, X, LogOut, ChevronRight, Home, GraduationCap, Users, LayoutDashboard, Briefcase, ShieldCheck } from "lucide-react";
import { useBrandingStore } from "../stores/branding";
import { LanguageSwitcher } from "./LanguageSwitcher";
import { t } from "../config/i18n";
export const AppShell = ({ children }) => {
    const { displayName, primaryColor, accentColor, logoUrl } = useBrandingStore();
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const navigate = useNavigate();
    const location = useLocation();
    // Hide shell on auth pages
    if (["/login", "/signup"].includes(location.pathname)) {
        return _jsx(_Fragment, { children: children });
    }
    const handleLogout = () => {
        localStorage.clear();
        navigate("/login");
    };
    const navItems = [
        { label: t('nav.home'), path: "/", icon: Home },
        { label: t('nav.dashboards'), path: "/dashboards", icon: LayoutDashboard },
        { label: t('nav.studentPulse'), path: "/student-pulse", icon: GraduationCap },
        { label: t('nav.teacherWorkspace'), path: "/teacher-workspace", icon: Briefcase },
        { label: t('nav.parentPortal'), path: "/parent-portal", icon: Users },
        { label: t('nav.admin'), path: "/admin", icon: ShieldCheck },
    ];
    return (_jsxs("div", { className: "min-h-screen bg-slate-50 text-slate-900 font-sans", children: [_jsx("header", { className: "sticky top-0 z-50 shadow-md transition-colors duration-300", style: { backgroundColor: primaryColor }, children: _jsxs("div", { className: "max-w-7xl mx-auto px-4 py-3 flex items-center justify-between text-white", children: [_jsxs(Link, { to: "/", className: "flex items-center gap-3 hover:opacity-90 transition-opacity", children: [logoUrl ? (_jsx("img", { src: logoUrl, alt: "Logo", className: "h-10 w-10 rounded-xl bg-white/10 p-1 backdrop-blur-sm" })) : (_jsx("div", { className: "h-10 w-10 rounded-xl flex items-center justify-center text-lg font-bold shadow-inner", style: { backgroundColor: accentColor }, children: (displayName || "").charAt(0) })), _jsxs("div", { children: [_jsx("h1", { className: "text-lg font-bold leading-tight tracking-tight", children: displayName }), _jsx("p", { className: "text-[10px] uppercase tracking-wider opacity-80 font-medium", children: "Enterprise OS" })] })] }), _jsxs("nav", { className: "hidden md:flex items-center gap-1", children: [navItems.map((item) => (_jsx(Link, { to: item.path, className: `px-3 py-2 rounded-lg text-sm font-medium transition-all ${location.pathname === item.path
                                        ? "bg-white/20 shadow-sm"
                                        : "hover:bg-white/10"}`, children: item.label }, item.path))), _jsxs("div", { className: "ml-4 flex items-center gap-3", children: [_jsx(LanguageSwitcher, {}), _jsx("button", { onClick: handleLogout, className: "p-2 hover:bg-white/10 rounded-full transition-colors text-white/90 hover:text-white", title: "Logout", children: _jsx(LogOut, { size: 20 }) })] })] }), _jsx("button", { onClick: () => setIsMenuOpen(!isMenuOpen), className: "md:hidden p-2 active:scale-95 transition-transform", children: isMenuOpen ? _jsx(X, { size: 24 }) : _jsx(Menu, { size: 24 }) })] }) }), isMenuOpen && (_jsx("div", { className: "fixed inset-0 z-40 md:hidden bg-slate-900/50 backdrop-blur-sm", onClick: () => setIsMenuOpen(false), children: _jsxs("div", { className: "absolute right-0 top-0 bottom-0 w-3/4 max-w-sm bg-white shadow-2xl p-6 flex flex-col gap-2", onClick: (e) => e.stopPropagation(), children: [_jsxs("div", { className: "flex justify-between items-center mb-6", children: [_jsx("span", { className: "text-lg font-bold text-slate-800", children: "Menu" }), _jsx("button", { onClick: () => setIsMenuOpen(false), className: "p-2 bg-slate-100 rounded-full", children: _jsx(X, { size: 20, className: "text-slate-600" }) })] }), navItems.map((item) => (_jsxs(Link, { to: item.path, onClick: () => setIsMenuOpen(false), className: `flex items-center justify-between p-3 rounded-xl transition-all ${location.pathname === item.path
                                ? "bg-blue-50 text-blue-700 border border-blue-100"
                                : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"}`, children: [_jsxs("div", { className: "flex items-center gap-3", children: [_jsx(item.icon, { size: 18 }), _jsx("span", { className: "font-medium", children: item.label })] }), location.pathname === item.path && _jsx(ChevronRight, { size: 16 })] }, item.path))), _jsx("div", { className: "mt-auto border-t pt-4", children: _jsxs("button", { onClick: handleLogout, className: "w-full flex items-center justify-center gap-2 p-3 rounded-xl bg-red-50 text-red-600 font-medium hover:bg-red-100 transition-colors", children: [_jsx(LogOut, { size: 18 }), t('nav.signOut')] }) })] }) })), _jsx("main", { className: "max-w-7xl mx-auto px-4 py-8 animate-fade-in", children: children })] }));
};
