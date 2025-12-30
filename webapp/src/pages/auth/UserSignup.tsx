import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, Mail, Lock, Phone, Camera, CheckCircle, ArrowRight } from 'lucide-react';
import { GoogleLogin, CredentialResponse } from '@react-oauth/google';
import clsx from 'clsx';

function decodeJwt(token: string) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function (c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        return JSON.parse(jsonPayload);
    } catch (e) {
        return null;
    }
}

interface SignupForm {
    email: string;
    password: string;
    confirm_password: string;
    first_name: string;
    last_name: string;
    phone: string;
    photo_url?: string;
}

export const UserSignup = () => {
    const navigate = useNavigate();
    const [step, setStep] = useState<'form' | 'success'>('form');
    const [loading, setLoading] = useState(false);
    const [isGoogleSignup, setIsGoogleSignup] = useState(false);
    const [googleCredential, setGoogleCredential] = useState<string>('');
    const [error, setError] = useState('');

    const [form, setForm] = useState<SignupForm>({
        email: '',
        password: '',
        confirm_password: '',
        first_name: '',
        last_name: '',
        phone: '',
        photo_url: ''
    });

    const handleGoogleSuccess = async (credentialResponse: CredentialResponse) => {
        if (!credentialResponse.credential) return;

        setLoading(true);
        setError('');

        try {
            const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
            const response = await fetch(`${apiUrl}/api/auth/google/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    credential: credentialResponse.credential
                })
            });

            const data = await response.json();

            if (data.success) {
                // Store tokens
                localStorage.setItem('access_token', data.access_token);
                localStorage.setItem('user_id', data.user.id);
                setStep('success');
            } else {
                setError(data.detail || 'Google Sign-In failed');
            }
        } catch (err) {
            setError('Connection failed. Please check internet and try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        // Validation
        if (form.password !== form.confirm_password) {
            setError('Passwords do not match');
            return;
        }

        if (form.password.length < 8) {
            setError('Password must be at least 8 characters');
            return;
        }

        // Bcrypt has a 72-byte limit
        if (form.password.length > 72) {
            setError('Password is too long. Maximum 72 characters.');
            return;
        }

        setLoading(true);

        try {
            const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';

            let response;
            if (isGoogleSignup) {
                // Google Sign-Up with phone number
                response = await fetch(`${apiUrl}/api/auth/google/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        credential: googleCredential,
                        phone: form.phone
                    })
                });
            } else {
                // Regular email/password signup
                response = await fetch(`${apiUrl}/api/auth/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        email: form.email,
                        password: form.password,
                        first_name: form.first_name,
                        last_name: form.last_name,
                        phone: form.phone,
                        photo_url: form.photo_url || null
                    })
                });
            }

            const data = await response.json();

            if (data.success) {
                // Store auth token
                localStorage.setItem('access_token', data.access_token);
                localStorage.setItem('user_id', data.user_id);
                setStep('success');
            } else {
                setError(data.detail || 'Registration failed. Please try again.');
            }
        } catch (err) {
            setError('Connection failed. Please check internet and try again.');
        } finally {
            setLoading(false);
        }
    };

    if (step === 'success') {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center p-6">
                <div className="bg-slate-800 border border-green-500/30 rounded-2xl p-8 max-w-2xl w-full">
                    <div className="text-center mb-6">
                        <CheckCircle size={64} className="mx-auto text-green-500 mb-4" />
                        <h1 className="text-3xl font-bold text-white mb-2">🎉 Account Created!</h1>
                        <p className="text-slate-300">Welcome to Angels AI School</p>
                    </div>

                    <div className="bg-slate-900 border border-slate-700 rounded-xl p-6 mb-6">
                        <h3 className="font-semibold text-white mb-4">What's next?</h3>
                        <p className="text-slate-300 mb-4">
                            Your personal account is ready. Now you can join a school or create your own.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <button
                            onClick={() => navigate('/join-school')}
                            className="bg-blue-600 hover:bg-blue-500 text-white p-4 rounded-xl transition-colors font-medium flex items-center justify-center gap-2"
                        >
                            Join a School <ArrowRight size={18} />
                        </button>
                        <button
                            onClick={() => navigate('/register-school')}
                            className="bg-slate-700 hover:bg-slate-600 text-white p-4 rounded-xl transition-colors font-medium"
                        >
                            Create a School
                        </button>
                    </div>

                    <button
                        onClick={() => navigate('/login')}
                        className="w-full mt-4 text-center text-slate-400 hover:text-slate-300 text-sm"
                    >
                        Skip for now → Go to Dashboard
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center p-6">
            <div className="bg-slate-800 border border-slate-700 rounded-2xl p-8 max-w-2xl w-full">
                <div className="text-center mb-8">
                    <User size={48} className="mx-auto text-blue-400 mb-4" />
                    <h1 className="text-3xl font-bold text-white mb-2">Create Your Account</h1>
                    <p className="text-slate-300">Join Angels AI School - For Teachers, Parents & Students</p>
                </div>

                {/* Google Sign-Up - Direct Registration */}
                <div className="bg-gradient-to-r from-blue-900/30 to-purple-900/30 border border-blue-500/30 rounded-xl p-6 mb-8">
                    <div className="text-center mb-4">
                        <h3 className="text-white font-semibold mb-2">🚀 Instant Sign-Up with Google</h3>
                        <p className="text-slate-300 text-sm">No password needed - register in one click!</p>
                    </div>
                    <div className="flex justify-center">
                        <GoogleLogin
                            onSuccess={handleGoogleSuccess}
                            onError={() => setError('Google Sign-In failed')}
                            theme="filled_blue"
                            shape="pill"
                            text="signup_with"
                        />
                    </div>
                </div>

                <div className="relative mb-8">
                    <div className="absolute inset-0 flex items-center">
                        <div className="w-full border-t border-slate-600"></div>
                    </div>
                    <div className="relative flex justify-center text-sm">
                        <span className="px-4 bg-slate-800 text-slate-400">Or sign up with email</span>
                    </div>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Personal Information */}
                    <div className="bg-slate-900 border border-slate-700 rounded-xl p-6">
                        <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
                            <User size={20} className="text-blue-400" />
                            Personal Information
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-2">First Name *</label>
                                <input
                                    type="text"
                                    required
                                    value={form.first_name}
                                    onChange={(e) => setForm({ ...form, first_name: e.target.value })}
                                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-2">Last Name *</label>
                                <input
                                    type="text"
                                    required
                                    value={form.last_name}
                                    onChange={(e) => setForm({ ...form, last_name: e.target.value })}
                                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                            <div className="md:col-span-2">
                                <label className="block text-sm font-medium text-slate-300 mb-2">Email *</label>
                                <input
                                    type="email"
                                    required
                                    value={form.email}
                                    onChange={(e) => setForm({ ...form, email: e.target.value })}
                                    placeholder="your@email.com"
                                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                            <div className="md:col-span-2">
                                <label className="block text-sm font-medium text-slate-300 mb-2">Phone *</label>
                                <input
                                    type="tel"
                                    required
                                    value={form.phone}
                                    onChange={(e) => setForm({ ...form, phone: e.target.value })}
                                    placeholder="+256 700 000 000"
                                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Security */}
                    <div className="bg-slate-900 border border-slate-700 rounded-xl p-6">
                        <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
                            <Lock size={20} className="text-blue-400" />
                            Security
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="md:col-span-2">
                                <label className="block text-sm font-medium text-slate-300 mb-2">Password *</label>
                                <input
                                    type="password"
                                    required
                                    value={form.password}
                                    onChange={(e) => setForm({ ...form, password: e.target.value })}
                                    placeholder="At least 8 characters"
                                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                            <div className="md:col-span-2">
                                <label className="block text-sm font-medium text-slate-300 mb-2">Confirm Password *</label>
                                <input
                                    type="password"
                                    required
                                    value={form.confirm_password}
                                    onChange={(e) => setForm({ ...form, confirm_password: e.target.value })}
                                    placeholder="Re-enter password"
                                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                        </div>
                    </div>



                    {error && (
                        <div className="p-3 bg-red-50 text-red-600 text-sm rounded-lg border border-red-100">
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white p-4 rounded-xl transition-colors font-medium text-lg flex items-center justify-center gap-2"
                    >
                        {loading ? (
                            <>
                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                Creating Account...
                            </>
                        ) : (
                            <>
                                Create Account <ArrowRight size={18} />
                            </>
                        )}
                    </button>
                </form>

                <p className="text-center text-slate-400 text-sm mt-6">
                    Already have an account? <a href="/login" className="text-blue-400 hover:underline">Login</a>
                </p>
            </div>
        </div>
    );
};
