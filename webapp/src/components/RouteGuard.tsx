/**
 * Route Guard Component
 * =====================
 * Enforces strict role-based isolation, effectively creating "Siloed Apps".
 */

import { Navigate, Outlet, useLocation } from "react-router-dom";
import { UserRole } from "../utils/manifestManager";

interface RouteGuardProps {
    allowedRoles: UserRole[];
}

export const RouteGuard = ({ allowedRoles }: RouteGuardProps) => {
    const location = useLocation();

    // In production, this would come from a secure Auth Context / JWT
    // For now, using localStorage as the source of truth for the demo
    const userRole = (localStorage.getItem("user_role") as UserRole) || "guest";
    const isAuthenticated = Boolean(localStorage.getItem("token"));

    if (!isAuthenticated) {
        // Redirect to signup/login, saving the attempted URL
        return <Navigate to="/signup" state={{ from: location }} replace />;
    }

    if (!allowedRoles.includes(userRole)) {
        console.warn(`⛔ Access Denied: Role '${userRole}' attempted to access protected route.`);
        // Redirect to their specific dashboard based on their role
        switch (userRole) {
            case "teacher": return <Navigate to="/teacher" replace />;
            case "parent": return <Navigate to="/parent" replace />;
            case "student": return <Navigate to="/student" replace />;
            case "admin": return <Navigate to="/admin" replace />;
            case "director": return <Navigate to="/director" replace />;
            default: return <Navigate to="/" replace />;
        }
    }

    // Authorized: Render the child routes
    return <Outlet />;
};
