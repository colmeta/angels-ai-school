import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useForm } from 'react-hook-form';
import { Lock, Mail, ArrowRight, School, User, Users, GraduationCap, Shield } from 'lucide-react';
import { useBrandingStore } from '../../stores/branding';
import { GoogleLogin } from '@react-oauth/google';
export const Login = () => {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const schoolId = searchParams.get('school') || 'default';
    const { displayName } = useBrandingStore();
    const [activeRole, setActiveRole] = useState('director');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const { register, handleSubmit } = useForm();
    const handleGoogleSuccess = async (credentialResponse) => {
        if (!credentialResponse.credential)
            return;
        setIsLoading(true);
        setError('');
        try {
            const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/auth/google/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    token: credentialResponse.credential
                })
            });
            const result = await response.json();
            if (result.access_token) {
                // Store session
                localStorage.setItem('access_token', result.access_token);
                localStorage.setItem('refresh_token', result.refresh_token);
                localStorage.setItem('user_role', result.user.role);
                localStorage.setItem('user_school', result.user.school_id);
                // Redirect based on role
                const roleRoutes = {
                    'admin': '/director',
                    'director': '/director',
                    'teacher': '/teacher',
                    'parent': '/parent',
                    'student': '/student',
                    'super_admin': '/admin'
                };
                navigate(roleRoutes[result.user.role] || '/');
            }
            else {
                setError(result.detail || 'Google authentication failed');
            }
        }
        catch (err) {
            setError('Google login failed. Please try again.');
            console.error(err);
        }
        finally {
            setIsLoading(false);
        }
    };
    const handleLogin = async (data) => {
        setIsLoading(true);
        setError('');
        try {
            const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email: data.email,
                    password: data.password,
                    school_id: schoolId
                })
            });
            const result = await response.json();
            if (result.success) {
                // Store session
                localStorage.setItem('access_token', result.access_token);
                localStorage.setItem('refresh_token', result.refresh_token);
                localStorage.setItem('user_role', result.user.role);
                localStorage.setItem('user_school', result.user.school_id);
                // Redirect based on role
                const roleRoutes = {
                    'admin': '/director', // Director is admin in backend
                    'director': '/director',
                    'teacher': '/teacher',
                    'parent': '/parent',
                    'student': '/student',
                    'super_admin': '/admin'
                };
                navigate(roleRoutes[result.user.role] || '/');
            }
            else {
                setError(result.detail || 'Invalid credentials');
            }
        }
        catch (err) {
            setError('Connection failed. Please check internet.');
            console.error(err);
        }
        finally {
            setIsLoading(false);
        }
    };
    const roles = [
        { id: 'director', label: 'Director', icon: School, color: 'bg-blue-600' },
        { id: 'teacher', label: 'Teacher', icon: User, color: 'bg-sky-500' },
        { id: 'parent', label: 'Parent', icon: Users, color: 'bg-emerald-500' },
        { id: 'student', label: 'Student', icon: GraduationCap, color: 'bg-violet-500' },
        { id: 'admin', label: 'Admin', icon: Shield, color: 'bg-slate-600' },
    ];
    return (_jsxs("div", { className: "min-h-screen flex bg-slate-50", children: [_jsxs("div", { className: "hidden lg:flex w-1/2 bg-slate-900 relative overflow-hidden items-center justify-center", children: [_jsx("div", { className: "absolute inset-0 bg-gradient-to-br from-blue-900 to-slate-900 opacity-90" }), _jsx("div", { className: "absolute inset-0 bg-[url('https://images.unsplash.com/photo-1523050854058-8df90110c9f1?q=80&w=2070')] bg-cover bg-center mix-blend-overlay" }), _jsx("div", { className: "relative z-10 text-white max-w-lg px-12", children: _jsxs(motion.div, { initial: { opacity: 0, y: 20 }, animate: { opacity: 1, y: 0 }, transition: { delay: 0.2 }, children: [_jsx("h1", { className: "text-5xl font-bold mb-6", children: displayName || 'Angels AI School' }), _jsx("p", { className: "text-xl text-slate-300 mb-8", children: "The Enterprise Operating System for modern education. Manage your entire school ecosystem in one place." }), _jsxs("div", { className: "flex gap-4", children: [_jsx("div", { className: "flex -space-x-4", children: [1, 2, 3, 4].map(i => (_jsx("div", { className: "w-10 h-10 rounded-full border-2 border-slate-900 bg-slate-700 flex items-center justify-center text-xs", children: "Uses AI" }, i))) }), _jsx("div", { className: "text-sm text-slate-400 mt-2", children: "Trusted by forward-thinking schools" })] })] }) })] }), _jsxs("div", { className: "w-full lg:w-1/2 flex items-center justify-center p-8 relative", children: [_jsx("div", { className: "max-w-md w-full relative z-10", children: _jsxs(motion.div, { initial: { opacity: 0, scale: 0.95 }, animate: { opacity: 1, scale: 1 }, children: [_jsxs("div", { className: "text-center mb-8 lg:text-left", children: [_jsx("h2", { className: "text-3xl font-bold text-slate-900", children: "Welcome back" }), _jsx("p", { className: "text-slate-500 mt-2", children: "Please sign in to your account" })] }), _jsx("div", { className: "mb-8 flex gap-2 overflow-x-auto pb-2 scrollbar-hide", children: roles.map((role) => (_jsxs("button", { onClick: () => setActiveRole(role.id), className: `flex flex-col items-center gap-2 p-3 min-w-[80px] rounded-xl border transition-all ${activeRole === role.id
                                            ? `${role.color} border-transparent text-white shadow-lg scale-105`
                                            : 'border-slate-200 text-slate-500 hover:border-slate-300 hover:bg-slate-50'}`, children: [_jsx(role.icon, { size: 20 }), _jsx("span", { className: "text-xs font-medium", children: role.label })] }, role.id))) }), _jsxs("form", { onSubmit: handleSubmit(handleLogin), className: "space-y-5", children: [_jsxs("div", { className: "space-y-1", children: [_jsx("label", { className: "text-sm font-medium text-slate-700", children: "Email Address" }), _jsxs("div", { className: "relative", children: [_jsx(Mail, { className: "absolute left-3 top-1/2 -translate-y-1/2 text-slate-400", size: 18 }), _jsx("input", { ...register('email'), type: "email", placeholder: "name@school.com", className: "w-full pl-10 pr-4 py-3 rounded-lg border border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all", required: true })] })] }), _jsxs("div", { className: "space-y-1", children: [_jsx("label", { className: "text-sm font-medium text-slate-700", children: "Password" }), _jsxs("div", { className: "relative", children: [_jsx(Lock, { className: "absolute left-3 top-1/2 -translate-y-1/2 text-slate-400", size: 18 }), _jsx("input", { ...register('password'), type: "password", placeholder: "\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022", className: "w-full pl-10 pr-4 py-3 rounded-lg border border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all", required: true })] }), _jsx("div", { className: "text-right", children: _jsx("a", { href: "#", className: "text-xs text-blue-600 hover:text-blue-700 font-medium", children: "Forgot password?" }) })] }), error && (_jsxs("div", { className: "p-3 bg-red-50 text-red-600 text-sm rounded-lg border border-red-100 flex items-center gap-2", children: [_jsx(Shield, { size: 16 }), error] })), _jsx("button", { type: "submit", disabled: isLoading, className: "w-full bg-slate-900 text-white py-3 rounded-lg font-semibold hover:bg-slate-800 active:scale-[0.98] transition-all flex items-center justify-center gap-2 shadow-lg shadow-slate-200", children: isLoading ? (_jsx("div", { className: "w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" })) : (_jsxs(_Fragment, { children: ["Sign In ", _jsx(ArrowRight, { size: 18 })] })) }), _jsxs("div", { className: "relative my-6", children: [_jsx("div", { className: "absolute inset-0 flex items-center", children: _jsx("div", { className: "w-full border-t border-slate-200" }) }), _jsx("div", { className: "relative flex justify-center text-sm", children: _jsx("span", { className: "px-2 bg-white text-slate-500", children: "Or continue with" }) })] }), _jsx("div", { className: "flex justify-center", children: _jsx(GoogleLogin, { onSuccess: handleGoogleSuccess, onError: () => setError('Google Sign-In was interrupted'), useOneTap: true, theme: "filled_blue", shape: "pill" }) })] }), _jsx("div", { className: "mt-8 text-center", children: _jsxs("p", { className: "text-slate-500 text-sm", children: ["New school?", ' ', _jsx("a", { href: "/signup", className: "text-blue-600 font-semibold hover:text-blue-700", children: "Register your school" })] }) })] }) }), _jsx("div", { className: "absolute top-0 right-0 -mt-20 -mr-20 w-80 h-80 bg-blue-100 rounded-full blur-3xl opacity-50 lg:hidden pointer-events-none" })] })] }));
};
