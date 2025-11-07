export const SupportOps = () => (
  <section className="space-y-6">
    <header className="space-y-2">
      <h1 className="text-2xl font-semibold">Support Operations Desk</h1>
      <p className="text-slate-300">
        Manage sickbay, library, transport, and incident reporting—even in low-connectivity zones.
      </p>
    </header>

    <div className="grid gap-4 md:grid-cols-2">
      <ActionCard
        title="Sickbay Log"
        description="Capture student health visits with a quick photo. Parents get notified instantly."
      />
      <ActionCard
        title="Library Scan"
        description="Use device camera to record book check-in/out. Inventory updates when you reconnect."
      />
      <ActionCard
        title="Transport Tracker"
        description="Mark bus departures and arrivals. Parents see “Bus arrived” notifications automatically."
      />
      <ActionCard
        title="Incident Report"
        description="Record security or discipline incidents with voice/text. Clarity prepares executive summaries."
      />
    </div>

    <div className="rounded-3xl border border-slate-800 bg-slate-900/60 p-6">
      <h2 className="text-lg font-semibold mb-2">Offline Queue Status</h2>
      <p className="text-sm text-slate-300">
        Every log is timestamped and assigned to the right agent (health, library, safety). Once you
        reconnect, supervisors receive a consolidated report.
      </p>
    </div>
  </section>
);

const ActionCard = ({ title, description }: { title: string; description: string }) => (
  <button className="rounded-3xl border border-slate-800 bg-slate-900/60 p-6 text-left transition hover:border-slate-700 hover:bg-slate-800">
    <h2 className="text-lg font-semibold mb-1">{title}</h2>
    <p className="text-sm text-slate-300">{description}</p>
  </button>
);
