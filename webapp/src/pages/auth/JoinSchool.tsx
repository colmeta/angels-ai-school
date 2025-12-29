import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { School, Hash, UserCircle, ArrowRight, CheckCircle, AlertCircle } from 'lucide-react';
import clsx from 'clsx';

export const JoinSchool = () => {
    const navigate = useNavigate();
    const [step, setStep] = useState<'entry' | 'success'>('entry');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [result, setResult] = useState<any>(null);

    const [schoolCode, setSchoolCode] = useState('');
    const [role, setRole] = useState<'student' | 'parent' | 'teacher' | 'staff'>('student');

    const handleJoin = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const userId = localStorage.getItem('user_id');
            const token = localStorage.getItem('access_token');

            if (!userId || !token) {
                setError('You must be logged in to join a school.');
                navigate('/login');
                return;
            }

            const apiUrl = import.meta.env.VITE_API_URL || '';
            const response = await fetch(`${apiUrl}/api/multi-school/user/${userId}/link-school`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    school_code: schoolCode,
                    role: role
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                setResult(data);
                setStep('success');
            } else {
                setError(data.error || data.detail || 'Failed to join school. Please check the code.');
            }
        } catch (err) {
            setError('Connection failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    if (step === 'success' && result) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center p-6">
                <div className="bg-slate-800 border border-green-500/30 rounded-2xl p-8 max-w-md w-full text-center">
                    <CheckCircle size={64} className="mx-auto text-green-500 mb-4" />
                    <h1 className="text-3xl font-bold text-white mb-2">Request Sent!</h1>
                    <p className="text-slate-300 mb-6">
                        {result.message}
                    </p>

                    <div className="bg-slate-900/50 rounded-xl p-4 mb-8 text-left border border-slate-700">
                        <p className="text-sm text-slate-400">School</p>
                        <p className="text-white font-semibold">{result.school_name}</p>
                        <p className="text-sm text-slate-400 mt-2">Role</p>
                        <p className="text-white capitalize font-semibold">{role}</p>
                    </div>

                    <button
                        onClick={() => navigate('/dashboards')}
                        className="w-full bg-blue-600 hover:bg-blue-500 text-white p-4 rounded-xl transition-colors font-medium flex items-center justify-center gap-2"
                    >
                        Go to Dashboard <ArrowRight size={18} />
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center p-6">
            <div className="bg-slate-800 border border-slate-700 rounded-2xl p-8 max-w-md w-full">
                <div className="text-center mb-8">
                    <School size={48} className="mx-auto text-blue-400 mb-4" />
                    <h1 className="text-3xl font-bold text-white mb-2">Join a School</h1>
                    <p className="text-slate-300">Enter the unique code provided by your school</p>
                </div>

                <form onSubmit={handleJoin} className="space-y-6">
                    <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2 flex items-center gap-2">
                            <Hash size={16} /> School Code (e.g. ABCD-1234)
                        </label>
                        <input
                            type="text"
                            required
                            placeholder="ABCD-1234"
                            value={schoolCode}
                            onChange={(e) => setSchoolCode(e.target.value.toUpperCase())}
                            className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white font-mono text-xl tracking-widest focus:outline-none focus:ring-2 focus:ring-blue-500 uppercase"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-300 mb-4 flex items-center gap-2">
                            <UserCircle size={16} /> I am a...
                        </label>
                        <div className="grid grid-cols-2 gap-3">
                            {['student', 'parent', 'teacher', 'staff'].map((r) => (
                                <button
                                    key={r}
                                    type="button"
                                    onClick={() => setRole(r as any)}
                                    className={clsx(
                                        "p-3 rounded-xl border text-sm font-medium transition-all",
                                        role === r
                                            ? "bg-blue-600 border-blue-500 text-white shadow-lg shadow-blue-500/20"
                                            : "bg-slate-900 border-slate-700 text-slate-400 hover:border-slate-500"
                                    )}
                                >
                                    {r.charAt(0).toUpperCase() + r.slice(1)}
                                </button>
                            ))}
                        </div>
                    </div>

                    {role === 'teacher' || role === 'staff' ? (
                        <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-4">
                            <p className="text-yellow-300 text-xs flex items-start gap-2">
                                <AlertCircle size={16} className="flex-shrink-0" />
                                <span>Note: Staff and Teacher roles require approval from the school director before you can access school data.</span>
                            </p>
                        </div>
                    ) : (
                        <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-4">
                            <p className="text-green-400 text-xs flex items-start gap-2">
                                <CheckCircle size={16} className="flex-shrink-0" />
                                <span>Note: Student and Parent roles are auto-approved for immediate access.</span>
                            </p>
                        </div>
                    )}

                    {error && (
                        <div className="p-3 bg-red-500/10 text-red-400 text-sm rounded-lg border border-red-500/20">
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={loading || !schoolCode}
                        className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white p-4 rounded-xl transition-colors font-medium text-lg flex items-center justify-center gap-2"
                    >
                        {loading ? 'Verifying Code...' : 'Join School →'}
                    </button>

                    <button
                        type="button"
                        onClick={() => navigate(-1)}
                        className="w-full text-slate-400 hover:text-slate-300 text-sm"
                    >
                        Back
                    </button>
                </form>
            </div>
        </div>
    );
};
