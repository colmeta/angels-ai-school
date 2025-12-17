import { Route, Routes } from "react-router-dom";

import { OfflineBanner } from "./components/OfflineBanner";
import { AppShell } from "./components/AppShell";
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
import { DirectorDashboard } from "./pages/dashboards/DirectorDashboard";
import { ClassDashboard } from "./pages/dashboards/ClassDashboard";
import { StudentProfile } from "./pages/dashboards/StudentProfile";
import { StaffProfile } from "./pages/dashboards/StaffProfile";
import { TemplateBuilder } from "./pages/tools/TemplateBuilder";
import { UniversalImport } from "./pages/tools/UniversalImport";
import { WhatsAppConfig } from "./pages/admin/WhatsAppConfig";

const DEFAULT_SCHOOL_ID = "angels-ai-demo";

const App = () => {
  const schoolId = useBrandingStore((state) => state.schoolId) ?? DEFAULT_SCHOOL_ID;
  useBranding(schoolId);
  useOfflineSync();

  return (
    <>
      <OfflineBanner />
      <AppShell>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/director" element={<DirectorDashboard />} />
          <Route path="/dashboard/class" element={<ClassDashboard />} />
          <Route path="/dashboard/student/:id" element={<StudentProfile />} />
          <Route path="/dashboard/staff/:id" element={<StaffProfile />} />
          <Route path="/teacher" element={<TeacherWorkspace />} />
          <Route path="/parent" element={<ParentPortal />} />
          <Route path="/student" element={<StudentPulse />} />
          <Route path="/support" element={<SupportOps />} />
          <Route path="/agents" element={<AgentsOverview />} />
          <Route path="/tools/template-builder" element={<TemplateBuilder />} />
          <Route path="/tools/import" element={<UniversalImport />} />
          <Route path="/admin/whatsapp-config" element={<WhatsAppConfig />} />
        </Routes>
      </AppShell>
    </>
  );
};

export default App;
