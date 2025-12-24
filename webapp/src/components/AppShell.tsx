import { ReactNode, useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { Menu, X, LogOut, ChevronRight, Home, Settings, GraduationCap, Users } from "lucide-react";
import { useBrandingStore } from "../stores/branding";
import { LanguageSwitcher } from "./LanguageSwitcher";

interface AppShellProps {
  children: ReactNode;
}

export const AppShell = ({ children }: AppShellProps) => {
  const { displayName, primaryColor, accentColor, logoUrl } = useBrandingStore();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  // Hide shell on auth pages
  if (["/login", "/signup"].includes(location.pathname)) {
    return <>{children}</>;
  }

  const handleLogout = () => {
    localStorage.clear();
    navigate("/login");
  };

  const navItems = [
    { label: "Home", path: "/", icon: Home },
    { label: "Admin", path: "/admin", icon: Settings },
    { label: "Director", path: "/director", icon: Users },
    { label: "Teacher", path: "/teacher", icon: GraduationCap },
    { label: "Parent", path: "/parent", icon: Users },
    { label: "Student", path: "/student", icon: GraduationCap },
  ];

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans">
      {/* Navbar */}
      <header
        className="sticky top-0 z-50 shadow-md transition-colors duration-300"
        style={{ backgroundColor: primaryColor }}
      >
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between text-white">
          {/* Logo & Brand */}
          <Link to="/" className="flex items-center gap-3 hover:opacity-90 transition-opacity">
            {logoUrl ? (
              <img src={logoUrl} alt="Logo" className="h-10 w-10 rounded-xl bg-white/10 p-1 backdrop-blur-sm" />
            ) : (
              <div
                className="h-10 w-10 rounded-xl flex items-center justify-center text-lg font-bold shadow-inner"
                style={{ backgroundColor: accentColor }}
              >
                {(displayName || "").charAt(0)}
              </div>
            )}
            <div>
              <h1 className="text-lg font-bold leading-tight tracking-tight">{displayName}</h1>
              <p className="text-[10px] uppercase tracking-wider opacity-80 font-medium">
                Enterprise OS
              </p>
            </div>
          </Link>

          {/* Desktop Nav */}
          <nav className="hidden md:flex items-center gap-1">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${location.pathname === item.path
                  ? "bg-white/20 shadow-sm"
                  : "hover:bg-white/10"
                  }`}
              >
                {item.label}
              </Link>
            ))}
            <div className="ml-4 flex items-center gap-3">
              <LanguageSwitcher />
              <button
                onClick={handleLogout}
                className="p-2 hover:bg-white/10 rounded-full transition-colors text-white/90 hover:text-white"
                title="Logout"
              >
                <LogOut size={20} />
              </button>
            </div>
          </nav>

          {/* Mobile Menu Toggle */}
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="md:hidden p-2 active:scale-95 transition-transform"
          >
            {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </header>

      {/* Mobile Drawer */}
      {isMenuOpen && (
        <div className="fixed inset-0 z-40 md:hidden bg-slate-900/50 backdrop-blur-sm" onClick={() => setIsMenuOpen(false)}>
          <div
            className="absolute right-0 top-0 bottom-0 w-3/4 max-w-sm bg-white shadow-2xl p-6 flex flex-col gap-2"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-center mb-6">
              <span className="text-lg font-bold text-slate-800">Menu</span>
              <button onClick={() => setIsMenuOpen(false)} className="p-2 bg-slate-100 rounded-full">
                <X size={20} className="text-slate-600" />
              </button>
            </div>

            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setIsMenuOpen(false)}
                className={`flex items-center justify-between p-3 rounded-xl transition-all ${location.pathname === item.path
                  ? "bg-blue-50 text-blue-700 border border-blue-100"
                  : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                  }`}
              >
                <div className="flex items-center gap-3">
                  <item.icon size={18} />
                  <span className="font-medium">{item.label}</span>
                </div>
                {location.pathname === item.path && <ChevronRight size={16} />}
              </Link>
            ))}

            <div className="mt-auto border-t pt-4">
              <button
                onClick={handleLogout}
                className="w-full flex items-center justify-center gap-2 p-3 rounded-xl bg-red-50 text-red-600 font-medium hover:bg-red-100 transition-colors"
              >
                <LogOut size={18} />
                Sign Out
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8 animate-fade-in">
        {children}
      </main>
    </div>
  );
};
