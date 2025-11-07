export const StudentPulse = () => (
  <section className="space-y-6">
    <header className="space-y-2">
      <h1 className="text-2xl font-semibold">Student Pulse Center</h1>
      <p className="text-slate-300">
        See assignments, attendance streaks, and request support. Built to work on shared devices
        with low bandwidth.
      </p>
    </header>

    <div className="grid gap-4 md:grid-cols-3">
      <PulseCard title="Attendance Streak" value="12 days" />
      <PulseCard title="Assignments Due" value="2" />
      <PulseCard title="Wellness Check-ins" value="All clear" />
    </div>

    <div className="grid gap-4 md:grid-cols-2">
      <div className="rounded-3xl border border-slate-800 bg-slate-900/60 p-6">
        <h2 className="text-lg font-semibold mb-2">Assignments</h2>
        <ul className="space-y-2 text-sm text-slate-300">
          <li>• Maths Revision (due Friday)</li>
          <li>• Social Studies Project (due next Tuesday)</li>
        </ul>
      </div>
      <div className="rounded-3xl border border-slate-800 bg-slate-900/60 p-6">
        <h2 className="text-lg font-semibold mb-2">Need Help?</h2>
        <p className="text-sm text-slate-300">
          Tap “Request Support” to notify your class teacher or counselor. Works offline and syncs
          when connected.
        </p>
        <button className="mt-4 rounded-full bg-emerald-500 px-4 py-2 text-sm font-semibold text-black hover:bg-emerald-400">
          Request Support
        </button>
      </div>
    </div>
  </section>
);

const PulseCard = ({ title, value }: { title: string; value: string }) => (
  <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
    <p className="text-xs uppercase tracking-wide text-slate-400">{title}</p>
    <p className="text-xl font-semibold mt-2">{value}</p>
  </div>
);
