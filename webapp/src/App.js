import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { Route, Routes } from "react-router-dom";
import { OfflineBanner } from "./components/OfflineBanner";
import { AppShell } from "./components/AppShell";
import { RouteGuard } from "./components/RouteGuard";
import { LandingPage } from "./pages/LandingPage";
import { Home } from "./pages/Home";
import { AdminDashboard } from "./pages/AdminDashboard";
import { TeacherWorkspace } from "./pages/TeacherWorkspace";
import { ParentPortal } from "./pages/ParentPortal";
import { StudentPulse } from "./pages/StudentPulse";
import { SupportOps } from "./pages/SupportOps";
import { AgentsOverview } from "./pages/AgentsOverview";
import { useBranding } from "./hooks/useBranding";
import { useBrandingStore } from "./stores/branding";
import { useOfflineSync } from "./hooks/useOfflineSync";
import { useDynamicManifest } from "./utils/manifestManager";
import { DirectorDashboard } from "./pages/dashboards/DirectorDashboard";
import { ClassDashboard } from "./pages/dashboards/ClassDashboard";
import { StudentProfile } from "./pages/dashboards/StudentProfile";
import { StaffProfile } from "./pages/dashboards/StaffProfile";
import { TemplateBuilder } from "./pages/tools/TemplateBuilder";
import { DocumentHub } from "./pages/tools/DocumentHub";
import { UniversalImport } from "./pages/tools/UniversalImport";
import { SmartScan } from "./components/SmartScan";
import { WhatsAppConfig } from "./pages/admin/WhatsAppConfig";
import { SchoolSignup } from "./pages/auth/SchoolSignup";
import { Login } from "./pages/auth/Login";
import { AILoader } from "./components/AILoader";
import { ExperimentService } from "./services/ExperimentService";
import { useEffect } from "react";
const DEFAULT_SCHOOL_ID = "angels-ai-demo";
const App = () => {
    const schoolId = useBrandingStore((state) => state.schoolId) ?? DEFAULT_SCHOOL_ID;
    useEffect(() => {
        // Enroll in A/B test if school ID is present
        if (schoolId) {
            ExperimentService.enrollInAIModeExperiment(schoolId);
        }
    }, [schoolId]);
    useBranding(schoolId);
    useDynamicManifest(); // Auto-switch PWA identity based on role
    useOfflineSync();
    return (_jsxs(_Fragment, { children: [_jsx(OfflineBanner, {}), _jsx(AILoader, {}), _jsx(AppShell, { children: _jsxs(Routes, { children: [_jsx(Route, { path: "/signup", element: _jsx(SchoolSignup, {}) }), _jsx(Route, { path: "/login", element: _jsx(Login, {}) }), _jsx(Route, { path: "/", element: _jsx(LandingPage, {}) }), _jsx(Route, { path: "/dashboards", element: _jsx(Home, {}) }), _jsx(Route, { path: "/tools/import", element: _jsx(UniversalImport, {}) }), _jsx(Route, { path: "/tools/scan", element: _jsx(SmartScan, {}) }), _jsxs(Route, { element: _jsx(RouteGuard, { allowedRoles: ["admin", "director"] }), children: [_jsx(Route, { path: "/admin", element: _jsx(AdminDashboard, {}) }), _jsx(Route, { path: "/admin/whatsapp-config", element: _jsx(WhatsAppConfig, {}) }), _jsx(Route, { path: "/agents", element: _jsx(AgentsOverview, {}) }), _jsx(Route, { path: "/tools/template-builder", element: _jsx(TemplateBuilder, {}) }), _jsx(Route, { path: "/tools/document-hub", element: _jsx(DocumentHub, {}) })] }), _jsxs(Route, { element: _jsx(RouteGuard, { allowedRoles: ["director", "admin"] }), children: [_jsx(Route, { path: "/director", element: _jsx(DirectorDashboard, {}) }), _jsx(Route, { path: "/dashboard/class", element: _jsx(ClassDashboard, {}) }), _jsx(Route, { path: "/dashboard/student/:id", element: _jsx(StudentProfile, {}) }), _jsx(Route, { path: "/dashboard/staff/:id", element: _jsx(StaffProfile, {}) })] }), _jsxs(Route, { element: _jsx(RouteGuard, { allowedRoles: ["teacher", "admin", "director"] }), children: [_jsx(Route, { path: "/teacher", element: _jsx(TeacherWorkspace, {}) }), _jsx(Route, { path: "/dashboard/class", element: _jsx(ClassDashboard, {}) }), " ", _jsx(Route, { path: "/dashboard/student/:id", element: _jsx(StudentProfile, {}) }), " "] }), _jsx(Route, { element: _jsx(RouteGuard, { allowedRoles: ["parent"] }), children: _jsx(Route, { path: "/parent", element: _jsx(ParentPortal, {}) }) }), _jsx(Route, { element: _jsx(RouteGuard, { allowedRoles: ["student"] }), children: _jsx(Route, { path: "/student", element: _jsx(StudentPulse, {}) }) }), _jsx(Route, { element: _jsx(RouteGuard, { allowedRoles: ["admin", "director"] }), children: _jsx(Route, { path: "/support", element: _jsx(SupportOps, {}) }) })] }) })] }));
};
export default App;
