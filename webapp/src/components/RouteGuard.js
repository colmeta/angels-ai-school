import { jsx as _jsx } from "react/jsx-runtime";
/**
 * Route Guard Component
 * =====================
 * Enforces strict role-based isolation, effectively creating "Siloed Apps".
 */
import { Navigate, Outlet, useLocation } from "react-router-dom";
export const RouteGuard = ({ allowedRoles }) => {
    const location = useLocation();
    // In production, this would come from a secure Auth Context / JWT
    // For now, using localStorage as the source of truth for the demo
    const userRole = localStorage.getItem("user_role") || "guest";
    const isAuthenticated = Boolean(localStorage.getItem("token"));
    if (!isAuthenticated) {
        // Redirect to signup/login, saving the attempted URL
        return _jsx(Navigate, { to: "/signup", state: { from: location }, replace: true });
    }
    if (!allowedRoles.includes(userRole)) {
        console.warn(`⛔ Access Denied: Role '${userRole}' attempted to access protected route.`);
        // Redirect to their specific dashboard based on their role
        switch (userRole) {
            case "teacher": return _jsx(Navigate, { to: "/teacher", replace: true });
            case "parent": return _jsx(Navigate, { to: "/parent", replace: true });
            case "student": return _jsx(Navigate, { to: "/student", replace: true });
            case "admin": return _jsx(Navigate, { to: "/admin", replace: true });
            case "director": return _jsx(Navigate, { to: "/director", replace: true });
            default: return _jsx(Navigate, { to: "/", replace: true });
        }
    }
    // Authorized: Render the child routes
    return _jsx(Outlet, {});
};
