import { ReactNode } from "react";
import { Link } from "react-router-dom";

import { useBrandingStore } from "../stores/branding";

interface AppShellProps {
  children: ReactNode;
}

export const AppShell = ({ children }: AppShellProps) => {
  const { displayName, primaryColor, accentColor, logoUrl } = useBrandingStore();

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50">
      <header
        className="flex items-center justify-between px-4 py-3"
        style={{ backgroundColor: primaryColor }}
      >
        <div className="flex items-center gap-3">
          {logoUrl ? (
            <img src={logoUrl} alt={`${displayName} logo`} className="h-10 w-10 rounded-full" />
          ) : (
            <div
              className="h-10 w-10 rounded-full flex items-center justify-center text-xl font-bold"
              style={{ backgroundColor: accentColor }}
            >
              {displayName.charAt(0)}
            </div>
          )}
          <div>
            <p className="text-lg font-semibold leading-tight">{displayName}</p>
            <p className="text-xs uppercase tracking-wide text-slate-200">
              Powered by Clarity Engine
            </p>
          </div>
        </div>
        <nav className="flex gap-3 text-sm font-semibold">
          <Link to="/" className="hover:text-slate-200">
            Home
          </Link>
          <Link to="/admin" className="hover:text-slate-200">
            Admin
          </Link>
          <Link to="/teacher" className="hover:text-slate-200">
            Teacher
          </Link>
          <Link to="/parent" className="hover:text-slate-200">
            Parent
          </Link>
          <Link to="/student" className="hover:text-slate-200">
            Student
          </Link>
          <Link to="/support" className="hover:text-slate-200">
            Support Staff
          </Link>
        </nav>
      </header>
      <main className="px-4 py-6 max-w-6xl mx-auto">{children}</main>
    </div>
  );
};
