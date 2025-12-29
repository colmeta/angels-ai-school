import React from 'react';
import { Sparkles, AlertTriangle, Calendar, ArrowRight } from 'lucide-react';

interface BriefingProps {
    role: 'admin' | 'parent';
}

const BriefingWidget: React.FC<BriefingProps> = ({ role }) => {
    return (
        <div className="bg-gradient-to-br from-blue-600 to-indigo-700 rounded-2xl p-6 text-white shadow-lg overflow-hidden relative">
            {/* Background Decorative Element */}
            <div className="absolute -right-8 -bottom-8 w-32 h-32 bg-white/10 rounded-full blur-2xl"></div>

            <div className="flex items-center gap-2 mb-4 opacity-90">
                <Sparkles className="w-5 h-5 text-yellow-300" />
                <span className="text-sm font-medium tracking-wide">YOUR MORNING BRIEFING</span>
            </div>

            <h2 className="text-xl font-bold mb-6">
                {role === 'admin' ? "Good Morning, Director. Here's your focus today." : "Good Day. Here's what's happening at school."}
            </h2>

            <div className="space-y-4">
                {role === 'admin' ? (
                    <>
                        <div className="flex items-start gap-4 bg-white/10 p-4 rounded-xl backdrop-blur-sm">
                            <AlertTriangle className="w-6 h-6 text-yellow-200 shrink-0" />
                            <div>
                                <p className="font-semibold text-sm">Action Required</p>
                                <p className="text-sm opacity-80">3 teachers haven't confirmed attendance for Sports Day.</p>
                            </div>
                        </div>
                        <div className="flex items-start gap-4 bg-white/10 p-4 rounded-xl backdrop-blur-sm">
                            <Calendar className="w-6 h-6 text-blue-200 shrink-0" />
                            <div>
                                <p className="font-semibold text-sm">Upcoming Highlight</p>
                                <p className="text-sm opacity-80">PTA Meeting starts at 2:00 PM. Your agenda is prepared.</p>
                            </div>
                        </div>
                    </>
                ) : (
                    <>
                        <div className="flex items-start gap-4 bg-white/10 p-4 rounded-xl backdrop-blur-sm">
                            <Calendar className="w-6 h-6 text-blue-200 shrink-0" />
                            <div>
                                <p className="font-semibold text-sm">Today's Event</p>
                                <p className="text-sm opacity-80">P.3 Sports Day @ 10:00 AM. Remember to pack the jersey!</p>
                            </div>
                        </div>
                    </>
                )}
            </div>

            <button className="mt-6 flex items-center gap-2 text-sm font-bold bg-white text-blue-700 px-4 py-2 rounded-full hover:bg-blue-50 transition-colors">
                View All Operations <ArrowRight className="w-4 h-4" />
            </button>
        </div>
    );
};

export default BriefingWidget;
