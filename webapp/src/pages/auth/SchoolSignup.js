import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { School, User, CheckCircle, AlertCircle } from 'lucide-react';
import { GoogleLogin } from '@react-oauth/google';
function decodeJwt(token) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function (c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        return JSON.parse(jsonPayload);
    }
    catch (e) {
        return null;
    }
}
export const SchoolSignup = () => {
    const [step, setStep] = useState('form');
    const [loading, setLoading] = useState(false);
    const [credentials, setCredentials] = useState(null);
    const [form, setForm] = useState({
        school_name: '',
        country: 'Uganda',
        address: '',
        phone: '',
        email: '',
        director_first_name: '',
        director_last_name: '',
        director_email: '',
        director_phone: '',
        student_count_estimate: 100,
        plan: 'free'
    });
    const handleGoogleSuccess = (credentialResponse) => {
        if (credentialResponse.credential) {
            const decoded = decodeJwt(credentialResponse.credential);
            if (decoded) {
                setForm(prev => ({
                    ...prev,
                    director_email: decoded.email || '',
                    director_first_name: decoded.given_name || '',
                    director_last_name: decoded.family_name || '',
                    email: prev.email || decoded.email || '' // Also suggest for school email if empty
                }));
            }
        }
    };
    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            // TODO: Replace with actual API call
            const response = await fetch('/api/schools/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(form)
            });
            const data = await response.json();
            if (data.success) {
                setCredentials({
                    email: data.admin_email,
                    password: data.temporary_password,
                    schoolId: data.school_id
                });
                setStep('success');
            }
        }
        catch (error) {
            alert('Registration failed. Please try again.');
        }
        finally {
            setLoading(false);
        }
    };
    if (step === 'success' && credentials) {
        return (_jsx("div", { className: "min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center p-6", children: _jsxs("div", { className: "bg-slate-800 border border-green-500/30 rounded-2xl p-8 max-w-2xl w-full", children: [_jsxs("div", { className: "text-center mb-6", children: [_jsx(CheckCircle, { size: 64, className: "mx-auto text-green-500 mb-4" }), _jsx("h1", { className: "text-3xl font-bold text-white mb-2", children: "\uD83C\uDF89 Welcome to Angels AI!" }), _jsx("p", { className: "text-slate-300", children: "Your school account is ready" })] }), _jsxs("div", { className: "bg-slate-900 border border-slate-700 rounded-xl p-6 mb-6", children: [_jsx("h3", { className: "font-semibold text-white mb-4", children: "Your Login Credentials" }), _jsxs("div", { className: "space-y-3", children: [_jsxs("div", { children: [_jsx("label", { className: "text-sm text-slate-400", children: "Email" }), _jsx("p", { className: "text-white font-mono bg-slate-800 p-2 rounded", children: credentials.email })] }), _jsxs("div", { children: [_jsx("label", { className: "text-sm text-slate-400", children: "Temporary Password" }), _jsx("p", { className: "text-white font-mono bg-slate-800 p-2 rounded", children: credentials.password })] }), _jsxs("div", { children: [_jsx("label", { className: "text-sm text-slate-400", children: "School ID" }), _jsx("p", { className: "text-white font-mono bg-slate-800 p-2 rounded text-xs", children: credentials.schoolId })] })] })] }), _jsx("div", { className: "bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-4 mb-6", children: _jsxs("p", { className: "text-yellow-300 text-sm flex items-start gap-2", children: [_jsx(AlertCircle, { size: 18, className: "flex-shrink-0 mt-0.5" }), _jsx("span", { children: "Please change your password after first login. We've also sent these credentials to your email." })] }) }), _jsxs("div", { className: "space-y-3", children: [_jsx("button", { onClick: () => window.location.href = '/login', className: "w-full bg-blue-600 hover:bg-blue-500 text-white p-4 rounded-xl transition-colors font-medium", children: "Go to Login" }), _jsx("a", { href: "/docs/getting-started", className: "block w-full text-center bg-slate-700 hover:bg-slate-600 text-white p-4 rounded-xl transition-colors", children: "View Setup Guide" })] })] }) }));
    }
    return (_jsx("div", { className: "min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center p-6", children: _jsxs("div", { className: "bg-slate-800 border border-slate-700 rounded-2xl p-8 max-w-4xl w-full", children: [_jsxs("div", { className: "text-center mb-8", children: [_jsx(School, { size: 48, className: "mx-auto text-blue-400 mb-4" }), _jsx("h1", { className: "text-3xl font-bold text-white mb-2", children: "Register Your School" }), _jsx("p", { className: "text-slate-300", children: "Start managing your school in 5 minutes" })] }), _jsxs("div", { className: "bg-slate-900/50 border border-slate-700 rounded-xl p-6 mb-8 flex flex-col items-center justify-center text-center", children: [_jsx("p", { className: "text-slate-300 mb-4 text-sm", children: "Quickly pre-fill your details with Google" }), _jsx("div", { className: "w-full max-w-xs", children: _jsx(GoogleLogin, { onSuccess: handleGoogleSuccess, onError: () => console.log('Login Failed'), theme: "filled_blue", shape: "pill", width: "100%", text: "signup_with" }) })] }), _jsxs("form", { onSubmit: handleSubmit, className: "space-y-6", children: [_jsxs("div", { className: "bg-slate-900 border border-slate-700 rounded-xl p-6", children: [_jsxs("h3", { className: "font-semibold text-white mb-4 flex items-center gap-2", children: [_jsx(School, { size: 20, className: "text-blue-400" }), "School Information"] }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 gap-4", children: [_jsxs("div", { className: "md:col-span-2", children: [_jsx("label", { className: "block text-sm font-medium text-slate-300 mb-2", children: "School Name *" }), _jsx("input", { type: "text", required: true, value: form.school_name, onChange: (e) => setForm({ ...form, school_name: e.target.value }), placeholder: "St. Mary's School", className: "w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-slate-300 mb-2", children: "Country *" }), _jsxs("select", { required: true, value: form.country, onChange: (e) => setForm({ ...form, country: e.target.value }), className: "w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500", children: [_jsx("option", { children: "Uganda" }), _jsx("option", { children: "Kenya" }), _jsx("option", { children: "Tanzania" }), _jsx("option", { children: "Rwanda" }), _jsx("option", { children: "Nigeria" }), _jsx("option", { children: "Other" })] })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-slate-300 mb-2", children: "Student Count *" }), _jsx("input", { type: "number", required: true, min: "10", value: form.student_count_estimate, onChange: (e) => setForm({ ...form, student_count_estimate: parseInt(e.target.value) }), className: "w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500" })] }), _jsxs("div", { className: "md:col-span-2", children: [_jsx("label", { className: "block text-sm font-medium text-slate-300 mb-2", children: "Address *" }), _jsx("input", { type: "text", required: true, value: form.address, onChange: (e) => setForm({ ...form, address: e.target.value }), placeholder: "Kampala, Uganda", className: "w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-slate-300 mb-2", children: "School Phone *" }), _jsx("input", { type: "tel", required: true, value: form.phone, onChange: (e) => setForm({ ...form, phone: e.target.value }), placeholder: "+256 700 000 000", className: "w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-slate-300 mb-2", children: "School Email *" }), _jsx("input", { type: "email", required: true, value: form.email, onChange: (e) => setForm({ ...form, email: e.target.value }), placeholder: "info@school.ac.ug", className: "w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500" })] })] })] }), _jsxs("div", { className: "bg-slate-900 border border-slate-700 rounded-xl p-6", children: [_jsxs("h3", { className: "font-semibold text-white mb-4 flex items-center gap-2", children: [_jsx(User, { size: 20, className: "text-blue-400" }), "Director/Admin Information"] }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 gap-4", children: [_jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-slate-300 mb-2", children: "First Name *" }), _jsx("input", { type: "text", required: true, value: form.director_first_name, onChange: (e) => setForm({ ...form, director_first_name: e.target.value }), className: "w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-slate-300 mb-2", children: "Last Name *" }), _jsx("input", { type: "text", required: true, value: form.director_last_name, onChange: (e) => setForm({ ...form, director_last_name: e.target.value }), className: "w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-slate-300 mb-2", children: "Email *" }), _jsx("input", { type: "email", required: true, value: form.director_email, onChange: (e) => setForm({ ...form, director_email: e.target.value }), placeholder: "director@school.ac.ug", className: "w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-slate-300 mb-2", children: "Phone *" }), _jsx("input", { type: "tel", required: true, value: form.director_phone, onChange: (e) => setForm({ ...form, director_phone: e.target.value }), placeholder: "+256 700 000 000", className: "w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500" })] })] })] }), _jsxs("div", { className: "bg-gradient-to-r from-green-500/20 via-blue-500/20 to-purple-500/20 border-2 border-green-500/50 rounded-xl p-8 text-center", children: [_jsx("div", { className: "inline-flex items-center justify-center w-16 h-16 bg-green-500 rounded-full mb-4", children: _jsx(CheckCircle, { size: 32, className: "text-white" }) }), _jsx("h3", { className: "text-2xl font-bold text-white mb-2", children: "100% Free Forever" }), _jsx("p", { className: "text-slate-300 mb-4", children: "All features, unlimited students, zero hidden costs" }), _jsx("div", { className: "grid grid-cols-2 md:grid-cols-4 gap-3 text-sm", children: [
                                        '✓ On-Device AI',
                                        '✓ Offline Mode',
                                        '✓ Cloud Sync',
                                        '✓ All Features',
                                        '✓ Unlimited Users',
                                        '✓ Priority Updates',
                                        '✓ Community Support',
                                        '✓ No Credit Card'
                                    ].map(feature => (_jsx("div", { className: "bg-slate-800/50 rounded-lg p-2 text-green-400", children: feature }, feature))) })] }), _jsx("button", { type: "submit", disabled: loading, className: "w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white p-4 rounded-xl transition-colors font-medium text-lg", children: loading ? 'Creating Your Account...' : 'Register School →' })] }), _jsxs("p", { className: "text-center text-slate-400 text-sm mt-6", children: ["Already have an account? ", _jsx("a", { href: "/login", className: "text-blue-400 hover:underline", children: "Login" })] })] }) }));
};
