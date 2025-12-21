import { useState } from 'react';
import { School, User, MapPin, Phone, Mail, Users, CheckCircle, AlertCircle } from 'lucide-react';
import clsx from 'clsx';

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
    plan: 'starter' | 'professional' | 'enterprise' | 'pilot';
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
        plan: 'pilot'
    });

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

                    {/* Plan Selection */}
                    <div className="bg-slate-900 border border-slate-700 rounded-xl p-6">
                        <h3 className="font-semibold text-white mb-4">Choose Your Plan</h3>
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                            {[
                                { id: 'pilot', name: 'Free Tier', price: '$0/student', features: ['All Features', 'Pilot Access'], recommended: true },
                                { id: 'starter', name: 'Starter', price: '$1/student', features: ['Basic Dashboard', 'Attendance', 'Fees'] },
                                { id: 'professional', name: 'Professional', price: '$2/student', features: ['All Starter +', 'Reports', 'WhatsApp'], recommended: false },
                                { id: 'enterprise', name: 'Enterprise', price: '$3/student', features: ['All Pro +', 'White Label', 'Priority Support'] }
                            ].map(plan => (
                                <label
                                    key={plan.id}
                                    className={clsx(
                                        "border-2 rounded-xl p-4 cursor-pointer transition-all relative",
                                        form.plan === plan.id ? "border-blue-500 bg-blue-500/10" : "border-slate-700 hover:border-slate-600"
                                    )}
                                >
                                    {plan.recommended && (
                                        <div className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-blue-500 text-white text-xs px-3 py-1 rounded-full">
                                            Recommended
                                        </div>
                                    )}
                                    <input
                                        type="radio"
                                        name="plan"
                                        value={plan.id}
                                        checked={form.plan === plan.id}
                                        onChange={(e) => setForm({ ...form, plan: e.target.value as any })}
                                        className="sr-only"
                                    />
                                    <div className="text-center">
                                        <h4 className="font-semibold text-white mb-1">{plan.name}</h4>
                                        <p className="text-blue-400 text-lg font-bold mb-3">{plan.price}</p>
                                        <ul className="text-sm text-slate-400 space-y-1">
                                            {plan.features.map(f => <li key={f}>• {f}</li>)}
                                        </ul>
                                    </div>
                                </label>
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
