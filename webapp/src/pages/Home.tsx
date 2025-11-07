import { Link } from "react-router-dom";

import { useBrandingStore } from "../stores/branding";

export const Home = () => {
  const { displayName, primaryColor, accentColor } = useBrandingStore();

  return (
    <section className="space-y-8">
      <div
        className="rounded-3xl p-8 text-slate-950 shadow-xl"
        style={{ background: `linear-gradient(135deg, ${primaryColor}, ${accentColor})` }}
      >
        <h1 className="text-3xl font-bold mb-2">{displayName}</h1>
        <p className="text-lg max-w-2xl">
          Your offline-first digital command center for African schools. Capture attendance,
          health updates, finances, and strategic intelligence—even without internet. Syncs to the
          Clarity engine the moment you reconnect.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <RoleCard
          title="Administrator"
          description="Daily briefings, finance cockpit, risk/compliance intelligence."
          link="/admin"
        />
        <RoleCard
          title="Teacher"
          description="Snap attendance or marks, auto-notify parents, generate reports instantly."
          link="/teacher"
        />
        <RoleCard
          title="Parent"
          description="Live child updates, mobile-money payments, chatbot answers without WhatsApp fees."
          link="/parent"
        />
        <RoleCard
          title="Student"
          description="View assignments, progress streaks, and wellness check-ins."
          link="/student"
        />
        <RoleCard
          title="Support Staff"
          description="Sickbay logs, library circulation, transport tracking, incident management."
          link="/support"
        />
        <RoleCard
          title="Executive Agent Crew"
          description="Meet the nine AI specialists orchestrated by Clarity, from CEO brain to safety guardian."
          link="/agents"
        />
      </div>
    </section>
  );
};

interface RoleCardProps {
  title: string;
  description: string;
  link: string;
}

const RoleCard = ({ title, description, link }: RoleCardProps) => (
  <Link
    to={link}
    className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 transition hover:border-slate-700 hover:bg-slate-800/80"
  >
    <h2 className="text-xl font-semibold mb-2">{title}</h2>
    <p className="text-sm text-slate-300">{description}</p>
  </Link>
);
