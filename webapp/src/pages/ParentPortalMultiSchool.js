import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * Enhanced Parent Portal with Multi-School Support
 * Shows combined view or individual school view
 */
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/apiClient';
import { SchoolSwitcher } from '@/components/SchoolSwitcher';
export function ParentPortalMultiSchool({ userId }) {
    const [selectedSchool, setSelectedSchool] = useState('all');
    const [isAllSchools, setIsAllSchools] = useState(true);
    // Fetch combined dashboard for all schools
    const { data: combinedData, isPending: loadingCombined } = useQuery({
        queryKey: ['combined-dashboard', userId],
        queryFn: async () => {
            const response = await apiClient.get(`/multi-school/user/${userId}/dashboard/combined`);
            return response.data;
        },
        enabled: isAllSchools,
    });
    // Fetch single school dashboard
    const { data: singleSchoolData, isPending: loadingSingle } = useQuery({
        queryKey: ['single-school-dashboard', userId, selectedSchool],
        queryFn: async () => {
            const response = await apiClient.get(`/${selectedSchool}/parent/${userId}/dashboard`);
            return response.data;
        },
        enabled: !isAllSchools && selectedSchool !== 'all',
    });
    const handleSchoolChange = (schoolId, isAll) => {
        setSelectedSchool(schoolId);
        setIsAllSchools(isAll);
    };
    const isLoading = isAllSchools ? loadingCombined : loadingSingle;
    return (_jsx("div", { className: "min-h-screen bg-gray-50 p-4", children: _jsxs("div", { className: "max-w-6xl mx-auto space-y-6", children: [_jsxs("div", { className: "flex items-center justify-between", children: [_jsxs("div", { children: [_jsx("h1", { className: "text-3xl font-bold text-gray-900", children: "Parent Portal" }), _jsx("p", { className: "text-gray-600 mt-1", children: "View your children's progress and school updates" })] }), _jsx(SchoolSwitcher, { userId: userId, currentSchoolId: selectedSchool, onSchoolChange: handleSchoolChange })] }), isLoading ? (_jsx("div", { className: "flex items-center justify-center h-64", children: _jsx("div", { className: "animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" }) })) : isAllSchools ? (_jsx(CombinedDashboard, { data: combinedData })) : (_jsx(SingleSchoolDashboard, { data: singleSchoolData, schoolId: selectedSchool }))] }) }));
}
function CombinedDashboard({ data }) {
    if (!data)
        return null;
    return (_jsxs("div", { className: "space-y-6", children: [_jsxs("div", { className: "grid grid-cols-1 md:grid-cols-3 gap-4", children: [_jsxs("div", { className: "bg-white rounded-lg shadow p-6", children: [_jsx("div", { className: "text-sm text-gray-600 mb-1", children: "Total Schools" }), _jsx("div", { className: "text-3xl font-bold text-gray-900", children: data.total_schools })] }), _jsxs("div", { className: "bg-white rounded-lg shadow p-6", children: [_jsx("div", { className: "text-sm text-gray-600 mb-1", children: "Total Children" }), _jsx("div", { className: "text-3xl font-bold text-gray-900", children: data.schools.reduce((sum, school) => sum + school.children.length, 0) })] }), _jsxs("div", { className: "bg-white rounded-lg shadow p-6", children: [_jsx("div", { className: "text-sm text-gray-600 mb-1", children: "Total Fees Due" }), _jsxs("div", { className: "text-3xl font-bold text-red-600", children: [(data.total_fee_balance || 0).toLocaleString(), " UGX"] })] })] }), data.schools.map((school) => (_jsxs("div", { className: "bg-white rounded-lg shadow overflow-hidden", children: [_jsx("div", { className: "bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4", children: _jsxs("h2", { className: "text-xl font-bold text-white", children: ["\uD83C\uDFEB ", school.brand_name || school.school_name] }) }), _jsx("div", { className: "p-6", children: school.children.length === 0 ? (_jsx("p", { className: "text-gray-500 text-center py-8", children: "No children at this school" })) : (_jsx("div", { className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4", children: school.children.map((child) => (_jsx("div", { className: "border border-gray-200 rounded-lg p-4 hover:border-blue-400 transition-colors", children: _jsxs("div", { className: "flex items-start gap-3", children: [_jsxs("div", { className: "w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-bold text-lg", children: [child.first_name[0], child.last_name[0]] }), _jsxs("div", { className: "flex-1", children: [_jsxs("div", { className: "font-semibold text-gray-900", children: [child.first_name, " ", child.last_name] }), _jsx("div", { className: "text-sm text-gray-600", children: child.class_name }), _jsxs("div", { className: "mt-2 space-y-1", children: [_jsxs("div", { className: "flex items-center justify-between text-sm", children: [_jsx("span", { className: "text-gray-600", children: "Today:" }), _jsx("span", { className: `font-medium ${child.attendance_today === 'present' ? 'text-green-600' :
                                                                        child.attendance_today === 'absent' ? 'text-red-600' :
                                                                            'text-gray-500'}`, children: child.attendance_today === 'present' ? '✅ Present' :
                                                                        child.attendance_today === 'absent' ? '❌ Absent' :
                                                                            '❓ Unknown' })] }), _jsxs("div", { className: "flex items-center justify-between text-sm", children: [_jsx("span", { className: "text-gray-600", children: "Fees:" }), _jsxs("span", { className: `font-medium ${child.fee_balance > 0 ? 'text-red-600' : 'text-green-600'}`, children: [child.fee_balance.toLocaleString(), " UGX"] })] }), child.recent_grade && (_jsxs("div", { className: "flex items-center justify-between text-sm", children: [_jsx("span", { className: "text-gray-600", children: "Recent:" }), _jsxs("span", { className: "font-medium text-blue-600", children: [child.recent_grade.marks_obtained, "/", child.recent_grade.max_marks, " (", child.recent_grade.grade, ")"] })] }))] })] })] }) }, child.id))) })) }), school.recent_notifications && school.recent_notifications.length > 0 && (_jsxs("div", { className: "border-t border-gray-200 px-6 py-4 bg-gray-50", children: [_jsx("h3", { className: "text-sm font-semibold text-gray-700 mb-3", children: "Recent Notifications" }), _jsx("div", { className: "space-y-2", children: school.recent_notifications.slice(0, 3).map((notif) => (_jsxs("div", { className: "text-sm", children: [_jsx("span", { className: "font-medium text-gray-900", children: notif.title }), _jsxs("span", { className: "text-gray-600", children: [" - ", notif.message] })] }, notif.id))) })] }))] }, school.school_id)))] }));
}
function SingleSchoolDashboard({ data, schoolId }) {
    if (!data)
        return null;
    // This would show the regular single-school parent portal
    // For now, just show basic info
    return (_jsxs("div", { className: "bg-white rounded-lg shadow p-6", children: [_jsx("h2", { className: "text-2xl font-bold text-gray-900 mb-4", children: "Single School View" }), _jsxs("p", { className: "text-gray-600", children: ["Showing data for school: ", schoolId] })] }));
}
