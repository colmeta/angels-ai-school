import { Route, Routes } from "react-router-dom";

import { OfflineBanner } from "./components/OfflineBanner";
import { AppShell } from "./components/AppShell";
import { RouteGuard } from "./components/RouteGuard";
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
import { UniversalImport } from "./pages/tools/UniversalImport";
import { WhatsAppConfig } from "./pages/admin/WhatsAppConfig";
import { SchoolSignup } from "./pages/auth/SchoolSignup";
import { Login } from "./pages/auth/Login";

const DEFAULT_SCHOOL_ID = "angels-ai-demo";

const App = () => {
  const schoolId = useBrandingStore((state) => state.schoolId) ?? DEFAULT_SCHOOL_ID;
  useBranding(schoolId);
  useDynamicManifest(); // Auto-switch PWA identity based on role
  useOfflineSync();

  return (
    <>
      <OfflineBanner />
      <AppShell>
        <Routes>
          {/* Public Routes */}
          <Route path="/signup" element={<SchoolSignup />} />
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<Home />} />
          <Route path="/tools/import" element={<UniversalImport />} />

          {/* 1. ADMIN OS (Core Config) */}
          <Route element={<RouteGuard allowedRoles={["admin", "director"]} />}>
            <Route path="/admin" element={<AdminDashboard />} />
            <Route path="/admin/whatsapp-config" element={<WhatsAppConfig />} />
            <Route path="/agents" element={<AgentsOverview />} />
            <Route path="/tools/template-builder" element={<TemplateBuilder />} />
          </Route>

          {/* 2. DIRECTOR SUITE (Analytics & Strategy) */}
          <Route element={<RouteGuard allowedRoles={["director", "admin"]} />}>
            <Route path="/director" element={<DirectorDashboard />} />
            {/* Directors can view deep profiles */}
            <Route path="/dashboard/class" element={<ClassDashboard />} />
            <Route path="/dashboard/student/:id" element={<StudentProfile />} />
            <Route path="/dashboard/staff/:id" element={<StaffProfile />} />
          </Route>

          {/* 3. TEACHER OS (Classroom Operations) */}
          <Route element={<RouteGuard allowedRoles={["teacher", "admin", "director"]} />}>
            <Route path="/teacher" element={<TeacherWorkspace />} />
            {/* Teachers can also access their specific class dashboards */}
            <Route path="/dashboard/class" element={<ClassDashboard />} /> {/* Shared */}
            <Route path="/dashboard/student/:id" element={<StudentProfile />} /> {/* Shared */}
          </Route>

          {/* 4. GUARDIAN PORTAL (Parent Access) */}
          <Route element={<RouteGuard allowedRoles={["parent"]} />}>
            <Route path="/parent" element={<ParentPortal />} />
          </Route>

          {/* 5. STUDENT PULSE (Learning) */}
          <Route element={<RouteGuard allowedRoles={["student"]} />}>
            <Route path="/student" element={<StudentPulse />} />
          </Route>

          {/* SUPPORT OPS (Restricted) */}
          <Route element={<RouteGuard allowedRoles={["admin", "director"]} />}>
            <Route path="/support" element={<SupportOps />} />
          </Route>

        </Routes>
      </AppShell>
    </>
  );
};

export default App;
