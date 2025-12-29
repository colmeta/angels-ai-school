import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";

import { useBrandingStore } from "../stores/branding";
import { useOfflineSync } from "../hooks/useOfflineSync";
import {
  adjustInventory,
  createHealthVisit,
  fetchHealthVisits,
  fetchIncidents,
  fetchInventorySnapshot,
  fetchLibraryTransactions,
  fetchSupportReport,
  fetchTransportEvents,
  logIncident,
  recordLibraryTransaction,
  recordTransportEvent,
} from "../lib/support";

export const SupportOps = () => {
  const schoolId = useBrandingStore((state) => state.schoolId);
  const { tasks, enqueueTask } = useOfflineSync();

  const [incidentForm, setIncidentForm] = useState({
    category: "Safety",
    severity: "medium",
    description: "",
    reported_by: "",
  });

  const [inventoryForm, setInventoryForm] = useState({
    item_name: "",
    change_quantity: 1,
    unit: "",
    reason: "",
    recorded_by: "",
  });

  const [healthForm, setHealthForm] = useState({
    student_name: "",
    grade: "",
    symptoms: "",
    action_taken: "",
    guardian_contacted: "",
    recorded_by: "",
  });

  const [libraryForm, setLibraryForm] = useState<{
    student_name: string;
    class_name: string;
    book_title: string;
    action: "borrow" | "return";
    due_date: string;
    recorded_by: string;
  }>({
    student_name: "",
    class_name: "",
    book_title: "",
    action: "borrow",
    due_date: "",
    recorded_by: "",
  });

  const [transportForm, setTransportForm] = useState({
    route_name: "",
    vehicle: "",
    status: "departed",
    notes: "",
    recorded_by: "",
  });

  const incidentsQuery = useQuery({
    queryKey: ["support-incidents", schoolId],
    queryFn: () => fetchIncidents(schoolId),
  });

  const inventoryQuery = useQuery({
    queryKey: ["support-inventory", schoolId],
    queryFn: () => fetchInventorySnapshot(schoolId),
  });

  const healthQuery = useQuery({
    queryKey: ["support-health", schoolId],
    queryFn: () => fetchHealthVisits(schoolId),
  });

  const libraryQuery = useQuery({
    queryKey: ["support-library", schoolId],
    queryFn: () => fetchLibraryTransactions(schoolId),
  });

  const transportQuery = useQuery({
    queryKey: ["support-transport", schoolId],
    queryFn: () => fetchTransportEvents(schoolId),
  });

  const reportQuery = useQuery({
    queryKey: ["support-report", schoolId],
    queryFn: () => fetchSupportReport(schoolId),
    refetchInterval: 1000 * 60 * 15,
  });

  const createIncidentMutation = useMutation({
    mutationFn: () => logIncident(schoolId, incidentForm),
    onSuccess: () => incidentsQuery.refetch(),
  });

  const adjustInventoryMutation = useMutation({
    mutationFn: () =>
      adjustInventory(schoolId, {
        ...inventoryForm,
        change_quantity: Number(inventoryForm.change_quantity),
      }),
    onSuccess: () => inventoryQuery.refetch(),
  });

  const recordHealthMutation = useMutation({
    mutationFn: () => createHealthVisit(schoolId, healthForm),
    onSuccess: () => healthQuery.refetch(),
  });

  const recordLibraryMutation = useMutation({
    mutationFn: () => recordLibraryTransaction(schoolId, libraryForm),
    onSuccess: () => libraryQuery.refetch(),
  });

  const recordTransportMutation = useMutation({
    mutationFn: () => recordTransportEvent(schoolId, transportForm),
    onSuccess: () => transportQuery.refetch(),
  });

  const pendingTasks = tasks.filter((task) =>
    task.endpoint.includes(`/support/${schoolId}`),
  );

  const handleSubmit = async (
    endpoint: string,
    body: Record<string, unknown>,
    mutation: { mutateAsync: () => Promise<unknown> },
    reset: () => void,
  ) => {
    if (!navigator.onLine) {
      enqueueTask(endpoint, body, "POST");
      reset();
      return;
    }
    await mutation.mutateAsync();
    reset();
  };

  return (
    <section className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-2xl font-semibold">Support Operations Desk</h1>
        <p className="text-slate-300">
          One hub for incidents, sickbay, inventory, transport, and library operations—works offline
          and syncs the moment you reconnect.
        </p>
      </header>

      <div className="grid gap-6 md:grid-cols-2">
        <FormCard
          title="Log Safety/Discipline Incident"
          description="Capture incidents as they happen; summaries go to leadership automatically."
        >
          <FormField label="Category">
            <input
              value={incidentForm.category}
              onChange={(event) => setIncidentForm({ ...incidentForm, category: event.target.value })}
              className="input"
            />
          </FormField>
          <FormField label="Severity">
            <select
              value={incidentForm.severity}
              onChange={(event) => setIncidentForm({ ...incidentForm, severity: event.target.value })}
              className="input"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </FormField>
          <FormField label="Description">
            <textarea
              value={incidentForm.description}
              onChange={(event) =>
                setIncidentForm({ ...incidentForm, description: event.target.value })
              }
              className="input"
            />
          </FormField>
          <FormField label="Reported By">
            <input
              value={incidentForm.reported_by}
              onChange={(event) =>
                setIncidentForm({ ...incidentForm, reported_by: event.target.value })
              }
              className="input"
            />
          </FormField>
          <SubmitButton
            text={navigator.onLine ? "Submit Incident" : "Queue Incident"}
            onClick={() =>
              handleSubmit(
                `/support/${schoolId}/incidents`,
                incidentForm,
                createIncidentMutation,
                () =>
                  setIncidentForm({
                    category: "Safety",
                    severity: "medium",
                    description: "",
                    reported_by: "",
                  }),
              )
            }
          />
        </FormCard>

        <FormCard
          title="Adjust Inventory / Expenses"
          description="Log stock movements for canteen, labs, or maintenance. Finance reports update instantly."
        >
          <FormField label="Item Name">
            <input
              value={inventoryForm.item_name}
              onChange={(event) =>
                setInventoryForm({ ...inventoryForm, item_name: event.target.value })
              }
              className="input"
            />
          </FormField>
          <FormField label="Quantity Change">
            <input
              type="number"
              value={inventoryForm.change_quantity}
              onChange={(event) =>
                setInventoryForm({ ...inventoryForm, change_quantity: Number(event.target.value) })
              }
              className="input"
            />
          </FormField>
          <FormField label="Unit (optional)">
            <input
              value={inventoryForm.unit}
              onChange={(event) => setInventoryForm({ ...inventoryForm, unit: event.target.value })}
              className="input"
            />
          </FormField>
          <FormField label="Reason">
            <textarea
              value={inventoryForm.reason}
              onChange={(event) =>
                setInventoryForm({ ...inventoryForm, reason: event.target.value })
              }
              className="input"
            />
          </FormField>
          <FormField label="Recorded By">
            <input
              value={inventoryForm.recorded_by}
              onChange={(event) =>
                setInventoryForm({ ...inventoryForm, recorded_by: event.target.value })
              }
              className="input"
            />
          </FormField>
          <SubmitButton
            text={navigator.onLine ? "Record Adjustment" : "Queue Adjustment"}
            onClick={() =>
              handleSubmit(
                `/support/${schoolId}/inventory/adjust`,
                inventoryForm,
                adjustInventoryMutation,
                () =>
                  setInventoryForm({
                    item_name: "",
                    change_quantity: 1,
                    unit: "",
                    reason: "",
                    recorded_by: "",
                  }),
              )
            }
          />
        </FormCard>

        <FormCard
          title="Sickbay / Health Visit"
          description="Log student visits to the sickbay. Parents can be notified automatically."
        >
          <FormField label="Student Name">
            <input
              value={healthForm.student_name}
              onChange={(event) =>
                setHealthForm({ ...healthForm, student_name: event.target.value })
              }
              className="input"
            />
          </FormField>
          <FormField label="Grade/Class">
            <input
              value={healthForm.grade}
              onChange={(event) => setHealthForm({ ...healthForm, grade: event.target.value })}
              className="input"
            />
          </FormField>
          <FormField label="Symptoms">
            <textarea
              value={healthForm.symptoms}
              onChange={(event) => setHealthForm({ ...healthForm, symptoms: event.target.value })}
              className="input"
            />
          </FormField>
          <FormField label="Action Taken">
            <textarea
              value={healthForm.action_taken}
              onChange={(event) =>
                setHealthForm({ ...healthForm, action_taken: event.target.value })
              }
              className="input"
            />
          </FormField>
          <FormField label="Guardian Contacted (optional)">
            <input
              value={healthForm.guardian_contacted}
              onChange={(event) =>
                setHealthForm({ ...healthForm, guardian_contacted: event.target.value })
              }
              className="input"
            />
          </FormField>
          <FormField label="Recorded By">
            <input
              value={healthForm.recorded_by}
              onChange={(event) =>
                setHealthForm({ ...healthForm, recorded_by: event.target.value })
              }
              className="input"
            />
          </FormField>
          <SubmitButton
            text={navigator.onLine ? "Save Health Visit" : "Queue Health Visit"}
            onClick={() =>
              handleSubmit(
                `/support/${schoolId}/health`,
                healthForm,
                recordHealthMutation,
                () =>
                  setHealthForm({
                    student_name: "",
                    grade: "",
                    symptoms: "",
                    action_taken: "",
                    guardian_contacted: "",
                    recorded_by: "",
                  }),
              )
            }
          />
        </FormCard>

        <FormCard
          title="Library Check-in/out"
          description="Snap a quick record when books are borrowed or returned. Inventory stays up to date."
        >
          <FormField label="Student Name">
            <input
              value={libraryForm.student_name}
              onChange={(event) =>
                setLibraryForm({ ...libraryForm, student_name: event.target.value })
              }
              className="input"
            />
          </FormField>
          <FormField label="Class">
            <input
              value={libraryForm.class_name}
              onChange={(event) =>
                setLibraryForm({ ...libraryForm, class_name: event.target.value })
              }
              className="input"
            />
          </FormField>
          <FormField label="Book Title">
            <input
              value={libraryForm.book_title}
              onChange={(event) =>
                setLibraryForm({ ...libraryForm, book_title: event.target.value })
              }
              className="input"
            />
          </FormField>
          <FormField label="Action">
            <select
              value={libraryForm.action}
              onChange={(event) =>
                setLibraryForm({ ...libraryForm, action: event.target.value as "borrow" | "return" })
              }
              className="input"
            >
              <option value="borrow">Borrow</option>
              <option value="return">Return</option>
            </select>
          </FormField>
          <FormField label="Due Date (optional)">
            <input
              type="date"
              value={libraryForm.due_date}
              onChange={(event) =>
                setLibraryForm({ ...libraryForm, due_date: event.target.value })
              }
              className="input"
            />
          </FormField>
          <FormField label="Recorded By">
            <input
              value={libraryForm.recorded_by}
              onChange={(event) =>
                setLibraryForm({ ...libraryForm, recorded_by: event.target.value })
              }
              className="input"
            />
          </FormField>
          <SubmitButton
            text={navigator.onLine ? "Record Transaction" : "Queue Transaction"}
            onClick={() =>
              handleSubmit(
                `/support/${schoolId}/library`,
                libraryForm,
                recordLibraryMutation,
                () =>
                  setLibraryForm({
                    student_name: "",
                    class_name: "",
                    book_title: "",
                    action: "borrow",
                    due_date: "",
                    recorded_by: "",
                  }),
              )
            }
          />
        </FormCard>

        <FormCard
          title="Transport Event"
          description="Track school transport departures and arrivals for parents and leadership."
        >
          <FormField label="Route Name">
            <input
              value={transportForm.route_name}
              onChange={(event) =>
                setTransportForm({ ...transportForm, route_name: event.target.value })
              }
              className="input"
            />
          </FormField>
          <FormField label="Vehicle (optional)">
            <input
              value={transportForm.vehicle}
              onChange={(event) =>
                setTransportForm({ ...transportForm, vehicle: event.target.value })
              }
              className="input"
            />
          </FormField>
          <FormField label="Status">
            <select
              value={transportForm.status}
              onChange={(event) =>
                setTransportForm({ ...transportForm, status: event.target.value })
              }
              className="input"
            >
              <option value="departed">Departed</option>
              <option value="arrived">Arrived</option>
              <option value="delayed">Delayed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </FormField>
          <FormField label="Notes (optional)">
            <textarea
              value={transportForm.notes}
              onChange={(event) =>
                setTransportForm({ ...transportForm, notes: event.target.value })
              }
              className="input"
            />
          </FormField>
          <FormField label="Recorded By">
            <input
              value={transportForm.recorded_by}
              onChange={(event) =>
                setTransportForm({ ...transportForm, recorded_by: event.target.value })
              }
              className="input"
            />
          </FormField>
          <SubmitButton
            text={navigator.onLine ? "Record Transport Event" : "Queue Transport Event"}
            onClick={() =>
              handleSubmit(
                `/support/${schoolId}/transport`,
                transportForm,
                recordTransportMutation,
                () =>
                  setTransportForm({
                    route_name: "",
                    vehicle: "",
                    status: "departed",
                    notes: "",
                    recorded_by: "",
                  }),
              )
            }
          />
        </FormCard>
      </div>

      <div className="rounded-3xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
        <h2 className="text-lg font-semibold">Offline Queue Status</h2>
        <p className="text-sm text-slate-300">
          Everything you queue offline appears below. The moment you reconnect, it auto-syncs and
          leadership receives the report.
        </p>
        {pendingTasks.length === 0 ? (
          <p className="text-xs text-slate-500">No queued tasks. You are fully synced.</p>
        ) : (
          <ul className="space-y-2 text-xs text-slate-200">
            {pendingTasks.map((task) => (
              <li key={task.id}>
                • {task.endpoint} — queued at {new Date(task.createdAt).toLocaleTimeString()}
              </li>
            ))}
          </ul>
        )}
      </div>

      <section className="grid gap-6 md:grid-cols-2">
        <LogCard
          title="Recent Incidents"
          items={incidentsQuery.data ?? []}
          render={(incident: any) => (
            <div>
              <p className="font-semibold text-sm">{incident.category}</p>
              <p className="text-xs text-slate-400">{incident.description}</p>
              <p className="text-[11px] uppercase text-slate-500 mt-1">
                Severity: {incident.severity} • Status: {incident.status}
              </p>
            </div>
          )}
        />

        <LogCard
          title="Inventory Snapshot"
          items={(inventoryQuery.data?.items ?? []).slice(0, 8)}
          render={(item: any) => (
            <div className="flex justify-between text-sm">
              <span>{item.item_name}</span>
              <span className="font-semibold">
                {item.current_quantity} {item.unit ?? ""}
              </span>
            </div>
          )}
        />

        <LogCard
          title="Sickbay Visits"
          items={healthQuery.data ?? []}
          render={(visit: any) => (
            <div>
              <p className="font-semibold text-sm">{visit.student_name}</p>
              <p className="text-xs text-slate-400">{visit.symptoms}</p>
              <p className="text-[11px] uppercase text-slate-500 mt-1">
                Action: {visit.action_taken}
              </p>
            </div>
          )}
        />

        <LogCard
          title="Transport Timeline"
          items={transportQuery.data ?? []}
          render={(event: any) => (
            <div>
              <p className="font-semibold text-sm">{event.route_name}</p>
              <p className="text-xs text-slate-400">{event.status}</p>
              <p className="text-[11px] uppercase text-slate-500 mt-1">
                Vehicle: {event.vehicle ?? "N/A"}
              </p>
            </div>
          )}
        />

        <LogCard
          title="Library Activity"
          items={libraryQuery.data ?? []}
          render={(entry: any) => (
            <div>
              <p className="font-semibold text-sm">{entry.book_title}</p>
              <p className="text-xs text-slate-400">
                {entry.student_name} • {entry.action}
              </p>
            </div>
          )}
        />
      </section>

      <section className="rounded-3xl border border-slate-800 bg-slate-900/60 p-6 space-y-2">
        <h2 className="text-lg font-semibold">Clarity Support Intelligence</h2>
        {reportQuery.isPending ? (
          <p className="text-sm text-slate-400">Generating report…</p>
        ) : reportQuery.data ? (
          <>
            <p className="text-sm text-slate-200">
              {reportQuery.data.analysis?.analysis?.summary ??
                reportQuery.data.analysis?.summary ??
                reportQuery.data.analysis?.analysis ??
                "Report ready."}
            </p>
            <p className="text-xs text-slate-500">
              Generated at {new Date(reportQuery.data.generated_at).toLocaleString()}
            </p>
          </>
        ) : (
          <p className="text-sm text-slate-400">
            No report yet. Capture a few records and we’ll assemble the briefing automatically.
          </p>
        )}
      </section>
    </section>
  );
};

const FormCard = ({
  title,
  description,
  children,
}: {
  title: string;
  description: string;
  children: React.ReactNode;
}) => (
  <div className="rounded-3xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
    <header>
      <h2 className="text-lg font-semibold">{title}</h2>
      <p className="text-xs text-slate-400">{description}</p>
    </header>
    <div className="space-y-3">{children}</div>
  </div>
);

const FormField = ({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) => (
  <label className="flex flex-col gap-1 text-sm">
    <span className="text-xs uppercase tracking-wide text-slate-400">{label}</span>
    {children}
  </label>
);

const SubmitButton = ({ text, onClick }: { text: string; onClick: () => void }) => (
  <button
    onClick={onClick}
    className="rounded-full bg-emerald-500 px-4 py-2 text-sm font-semibold text-black hover:bg-emerald-400"
  >
    {text}
  </button>
);

const LogCard = ({
  title,
  items,
  render,
}: {
  title: string;
  items: any[];
  render: (item: any) => React.ReactNode;
}) => (
  <div className="rounded-3xl border border-slate-800 bg-slate-900/60 p-5 space-y-3">
    <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-400">{title}</h3>
    {items.length === 0 ? (
      <p className="text-xs text-slate-500">No entries yet.</p>
    ) : (
      <div className="space-y-2 text-sm text-slate-200">
        {items.map((item, idx) => (
          <div key={idx} className="rounded-2xl border border-slate-800/60 bg-slate-950/50 p-3">
            {render(item)}
          </div>
        ))}
      </div>
    )}
  </div>
);

