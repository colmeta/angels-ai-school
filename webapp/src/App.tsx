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
          <Route path="/teacher" element={<TeacherWorkspace />} />
          <Route path="/parent" element={<ParentPortal />} />
          <Route path="/student" element={<StudentPulse />} />
          <Route path="/support" element={<SupportOps />} />
          <Route path="/agents" element={<AgentsOverview />} />
        </Routes>
      </AppShell>
    </>
  );
};

export default App;
