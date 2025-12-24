import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
/**
 * Role Switcher Component
 * Allows users with multiple roles at same school to switch between them
 * Example: Teacher who is also a parent switches between Teacher Mode and Parent Mode
 */
import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/apiClient';
const ROLE_CONFIG = {
    teacher: {
        label: 'Teacher Mode',
        icon: '🧑‍🏫',
        description: 'Manage classes, mark attendance, enter grades',
    },
    parent: {
        label: 'Parent Mode',
        icon: '👨‍👧',
        description: 'View children, pay fees, chat with teachers',
    },
    admin: {
        label: 'Admin Mode',
        icon: '⚙️',
        description: 'School settings, users, analytics',
    },
    staff: {
        label: 'Staff Mode',
        icon: '👔',
        description: 'Inventory, library, support',
    },
    student: {
        label: 'Student Mode',
        icon: '🎓',
        description: 'View grades, assignments, timetable',
    },
};
export function RoleSwitcher({ userId, schoolId, onRoleChange }) {
    const [isOpen, setIsOpen] = useState(false);
    const [selectedRole, setSelectedRole] = useState('');
    const queryClient = useQueryClient();
    // Fetch user's roles at this school
    const { data: rolesData, isLoading } = useQuery({
        queryKey: ['user-roles', userId, schoolId],
        queryFn: async () => {
            const response = await apiClient.get(`/multi-role/user/${userId}/school/${schoolId}/roles`);
            return response.data;
        },
    });
    // Switch role mutation
    const switchRoleMutation = useMutation({
        mutationFn: async (newRole) => {
            const response = await apiClient.post(`/multi-role/user/${userId}/switch-role`, {
                school_id: schoolId,
                new_role: newRole,
            });
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['user-roles', userId, schoolId] });
            queryClient.invalidateQueries({ queryKey: ['dashboard'] });
        },
    });
    const roles = rolesData?.roles || [];
    const hasMultipleRoles = roles.length > 1;
    const preferredRole = rolesData?.preferred_role;
    // Set initial role
    useEffect(() => {
        if (preferredRole && !selectedRole) {
            setSelectedRole(preferredRole);
        }
        else if (roles.length > 0 && !selectedRole) {
            setSelectedRole(roles[0]);
        }
    }, [preferredRole, roles, selectedRole]);
    const handleRoleSelect = (role) => {
        setSelectedRole(role);
        setIsOpen(false);
        switchRoleMutation.mutate(role);
        onRoleChange?.(role);
    };
    if (isLoading) {
        return (_jsx("div", { className: "animate-pulse bg-gray-200 h-12 rounded-lg w-48" }));
    }
    // If user has only one role, don't show switcher
    if (!hasMultipleRoles) {
        return null;
    }
    const currentRoleConfig = ROLE_CONFIG[selectedRole] || {
        label: selectedRole,
        icon: '👤',
        description: '',
    };
    return (_jsxs("div", { className: "relative", children: [_jsxs("button", { onClick: () => setIsOpen(!isOpen), className: "flex items-center gap-3 px-4 py-3 bg-white border-2 border-gray-200 rounded-lg shadow-sm hover:border-blue-400 transition-colors min-w-[240px]", children: [_jsx("div", { className: "text-2xl", children: currentRoleConfig.icon }), _jsxs("div", { className: "flex-1 text-left", children: [_jsx("div", { className: "text-sm font-semibold text-gray-900", children: currentRoleConfig.label }), _jsxs("div", { className: "text-xs text-gray-500", children: [roles.length, " ", roles.length === 1 ? 'role' : 'roles', " available"] })] }), _jsx("svg", { className: `w-5 h-5 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`, fill: "none", stroke: "currentColor", viewBox: "0 0 24 24", children: _jsx("path", { strokeLinecap: "round", strokeLinejoin: "round", strokeWidth: 2, d: "M19 9l-7 7-7-7" }) })] }), isOpen && (_jsxs(_Fragment, { children: [_jsx("div", { className: "fixed inset-0 z-40", onClick: () => setIsOpen(false) }), _jsxs("div", { className: "absolute top-full left-0 right-0 mt-2 bg-white border-2 border-gray-200 rounded-lg shadow-xl z-50 overflow-hidden", children: [_jsxs("div", { className: "p-3 bg-gray-50 border-b", children: [_jsx("div", { className: "text-sm font-semibold text-gray-700", children: "Switch View" }), _jsxs("div", { className: "text-xs text-gray-500", children: ["You have ", roles.length, " roles at this school"] })] }), roles.map((role) => {
                                const config = ROLE_CONFIG[role] || {
                                    label: role,
                                    icon: '👤',
                                    description: '',
                                };
                                const isSelected = role === selectedRole;
                                return (_jsx("button", { onClick: () => handleRoleSelect(role), className: `w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors border-b last:border-b-0 ${isSelected ? 'bg-blue-50' : ''}`, children: _jsxs("div", { className: "flex items-center gap-3", children: [_jsx("div", { className: "text-2xl", children: config.icon }), _jsxs("div", { className: "flex-1", children: [_jsx("div", { className: "text-sm font-semibold text-gray-900", children: config.label }), _jsx("div", { className: "text-xs text-gray-500", children: config.description })] }), isSelected && (_jsx("svg", { className: "w-5 h-5 text-blue-600", fill: "currentColor", viewBox: "0 0 20 20", children: _jsx("path", { fillRule: "evenodd", d: "M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z", clipRule: "evenodd" }) }))] }) }, role));
                            }), _jsx("div", { className: "p-3 bg-blue-50 text-xs text-blue-700", children: "\uD83D\uDCA1 Tip: Your selected role will be remembered for next time" })] })] })), switchRoleMutation.isPending && (_jsx("div", { className: "absolute inset-0 bg-white bg-opacity-75 rounded-lg flex items-center justify-center", children: _jsx("div", { className: "animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600" }) }))] }));
}
