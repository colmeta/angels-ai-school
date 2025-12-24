import { useState } from 'react';
import { School, User, MapPin, Phone, Mail, Users, CheckCircle, AlertCircle } from 'lucide-react';
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

interface RegistrationForm {
    school_name: string;
    country: string;
    address: string;
    phone: string;
    email: string;
    director_first_name: string;
    director_last_name: string;
    director_email: string;
    director_phone: string;
    student_count_estimate: number;
    plan: 'free';
}

export const SchoolSignup = () => {
    const [step, setStep] = useState<'form' | 'success'>('form');
    const [loading, setLoading] = useState(false);
    const [credentials, setCredentials] = useState<{ email: string; password: string; schoolId: string } | null>(null);

    const [form, setForm] = useState<RegistrationForm>({
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

    const handleGoogleSuccess = (credentialResponse: CredentialResponse) => {
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

    const handleSubmit = async (e: React.FormEvent) => {
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
        } catch (error) {
            alert('Registration failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    if (step === 'success' && credentials) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center p-6">
                <div className="bg-slate-800 border border-green-500/30 rounded-2xl p-8 max-w-2xl w-full">
                    <div className="text-center mb-6">
                        <CheckCircle size={64} className="mx-auto text-green-500 mb-4" />
                        <h1 className="text-3xl font-bold text-white mb-2">🎉 Welcome to Angels AI!</h1>
                        <p className="text-slate-300">Your school account is ready</p>
                    </div>

                    <div className="bg-slate-900 border border-slate-700 rounded-xl p-6 mb-6">
                        <h3 className="font-semibold text-white mb-4">Your Login Credentials</h3>
                        <div className="space-y-3">
                            <div>
                                <label className="text-sm text-slate-400">Email</label>
                                <p className="text-white font-mono bg-slate-800 p-2 rounded">{credentials.email}</p>
                            </div>
                            <div>
                                <label className="text-sm text-slate-400">Temporary Password</label>
                                <p className="text-white font-mono bg-slate-800 p-2 rounded">{credentials.password}</p>
                            </div>
                            <div>
                                <label className="text-sm text-slate-400">School ID</label>
                                <p className="text-white font-mono bg-slate-800 p-2 rounded text-xs">{credentials.schoolId}</p>
                            </div>
                        </div>
                    </div>

                    <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-4 mb-6">
                        <p className="text-yellow-300 text-sm flex items-start gap-2">
                            <AlertCircle size={18} className="flex-shrink-0 mt-0.5" />
                            <span>Please change your password after first login. We've also sent these credentials to your email.</span>
                        </p>
                    </div>

                    <div className="space-y-3">
                        <button
                            onClick={() => window.location.href = '/login'}
                            className="w-full bg-blue-600 hover:bg-blue-500 text-white p-4 rounded-xl transition-colors font-medium"
                        >
                            Go to Login
                        </button>
                        <a
                            href="/docs/getting-started"
                            className="block w-full text-center bg-slate-700 hover:bg-slate-600 text-white p-4 rounded-xl transition-colors"
                        >
                            View Setup Guide
                        </a>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center p-6">
            <div className="bg-slate-800 border border-slate-700 rounded-2xl p-8 max-w-4xl w-full">
                <div className="text-center mb-8">
                    <School size={48} className="mx-auto text-blue-400 mb-4" />
                    <h1 className="text-3xl font-bold text-white mb-2">Register Your School</h1>
                    <p className="text-slate-300">Start managing your school in 5 minutes</p>
                </div>

                <div className="bg-slate-900/50 border border-slate-700 rounded-xl p-6 mb-8 flex flex-col items-center justify-center text-center">
                    <p className="text-slate-300 mb-4 text-sm">Quickly pre-fill your details with Google</p>
                    <div className="w-full max-w-xs">
                        <GoogleLogin
                            onSuccess={handleGoogleSuccess}
                            onError={() => console.log('Login Failed')}
                            theme="filled_blue"
                            shape="pill"
                            width="100%"
                            text="signup_with"
                        />
                    </div>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                    {/* School Information */}
                    <div className="bg-slate-900 border border-slate-700 rounded-xl p-6">
                        <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
                            <School size={20} className="text-blue-400" />
                            School Information
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="md:col-span-2">
                                <label className="block text-sm font-medium text-slate-300 mb-2">School Name *</label>
                                <input
                                    type="text"
                                    required
                                    value={form.school_name}
                                    onChange={(e) => setForm({ ...form, school_name: e.target.value })}
                                    placeholder="St. Mary's School"
                                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-2">Country *</label>
                                <select
                                    required
                                    value={form.country}
                                    onChange={(e) => setForm({ ...form, country: e.target.value })}
                                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                                >
                                    <option>Uganda</option>
                                    <option>Kenya</option>
                                    <option>Tanzania</option>
                                    <option>Rwanda</option>
                                    <option>Nigeria</option>
                                    <option>Other</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-2">Student Count *</label>
                                <input
                                    type="number"
                                    required
                                    min="10"
                                    value={form.student_count_estimate}
                                    onChange={(e) => setForm({ ...form, student_count_estimate: parseInt(e.target.value) })}
                                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                            <div className="md:col-span-2">
                                <label className="block text-sm font-medium text-slate-300 mb-2">Address *</label>
                                <input
                                    type="text"
                                    required
                                    value={form.address}
                                    onChange={(e) => setForm({ ...form, address: e.target.value })}
                                    placeholder="Kampala, Uganda"
                                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-2">School Phone *</label>
                                <input
                                    type="tel"
                                    required
                                    value={form.phone}
                                    onChange={(e) => setForm({ ...form, phone: e.target.value })}
                                    placeholder="+256 700 000 000"
                                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-2">School Email *</label>
                                <input
                                    type="email"
                                    required
                                    value={form.email}
                                    onChange={(e) => setForm({ ...form, email: e.target.value })}
                                    placeholder="info@school.ac.ug"
                                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Director Information */}
                    <div className="bg-slate-900 border border-slate-700 rounded-xl p-6">
                        <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
                            <User size={20} className="text-blue-400" />
                            Director/Admin Information
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-2">First Name *</label>
                                <input
                                    type="text"
                                    required
                                    value={form.director_first_name}
                                    onChange={(e) => setForm({ ...form, director_first_name: e.target.value })}
                                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-2">Last Name *</label>
                                <input
                                    type="text"
                                    required
                                    value={form.director_last_name}
                                    onChange={(e) => setForm({ ...form, director_last_name: e.target.value })}
                                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-2">Email *</label>
                                <input
                                    type="email"
                                    required
                                    value={form.director_email}
                                    onChange={(e) => setForm({ ...form, director_email: e.target.value })}
                                    placeholder="director@school.ac.ug"
                                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-2">Phone *</label>
                                <input
                                    type="tel"
                                    required
                                    value={form.director_phone}
                                    onChange={(e) => setForm({ ...form, director_phone: e.target.value })}
                                    placeholder="+256 700 000 000"
                                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                        </div>
                    </div>

                    {/* 100% Free Platform Badge */}
                    <div className="bg-gradient-to-r from-green-500/20 via-blue-500/20 to-purple-500/20 border-2 border-green-500/50 rounded-xl p-8 text-center">
                        <div className="inline-flex items-center justify-center w-16 h-16 bg-green-500 rounded-full mb-4">
                            <CheckCircle size={32} className="text-white" />
                        </div>
                        <h3 className="text-2xl font-bold text-white mb-2">100% Free Forever</h3>
                        <p className="text-slate-300 mb-4">
                            All features, unlimited students, zero hidden costs
                        </p>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                            {[
                                '✓ On-Device AI',
                                '✓ Offline Mode',
                                '✓ Cloud Sync',
                                '✓ All Features',
                                '✓ Unlimited Users',
                                '✓ Priority Updates',
                                '✓ Community Support',
                                '✓ No Credit Card'
                            ].map(feature => (
                                <div key={feature} className="bg-slate-800/50 rounded-lg p-2 text-green-400">
                                    {feature}
                                </div>
                            ))}
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white p-4 rounded-xl transition-colors font-medium text-lg"
                    >
                        {loading ? 'Creating Your Account...' : 'Register School →'}
                    </button>
                </form>

                <p className="text-center text-slate-400 text-sm mt-6">
                    Already have an account? <a href="/login" className="text-blue-400 hover:underline">Login</a>
                </p>
            </div>
        </div>
    );
};
