import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useBrandingStore } from "../stores/branding";
import { useOfflineSync } from "../hooks/useOfflineSync";
import { adjustInventory, createHealthVisit, fetchHealthVisits, fetchIncidents, fetchInventorySnapshot, fetchLibraryTransactions, fetchSupportReport, fetchTransportEvents, logIncident, recordLibraryTransaction, recordTransportEvent, } from "../lib/support";
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
    const [libraryForm, setLibraryForm] = useState({
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
        mutationFn: () => adjustInventory(schoolId, {
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
    const pendingTasks = tasks.filter((task) => task.endpoint.includes(`/support/${schoolId}`));
    const handleSubmit = async (endpoint, body, mutation, reset) => {
        if (!navigator.onLine) {
            enqueueTask(endpoint, body, "POST");
            reset();
            return;
        }
        await mutation.mutateAsync();
        reset();
    };
    return (_jsxs("section", { className: "space-y-6", children: [_jsxs("header", { className: "space-y-2", children: [_jsx("h1", { className: "text-2xl font-semibold", children: "Support Operations Desk" }), _jsx("p", { className: "text-slate-300", children: "One hub for incidents, sickbay, inventory, transport, and library operations\u2014works offline and syncs the moment you reconnect." })] }), _jsxs("div", { className: "grid gap-6 md:grid-cols-2", children: [_jsxs(FormCard, { title: "Log Safety/Discipline Incident", description: "Capture incidents as they happen; summaries go to leadership automatically.", children: [_jsx(FormField, { label: "Category", children: _jsx("input", { value: incidentForm.category, onChange: (event) => setIncidentForm({ ...incidentForm, category: event.target.value }), className: "input" }) }), _jsx(FormField, { label: "Severity", children: _jsxs("select", { value: incidentForm.severity, onChange: (event) => setIncidentForm({ ...incidentForm, severity: event.target.value }), className: "input", children: [_jsx("option", { value: "low", children: "Low" }), _jsx("option", { value: "medium", children: "Medium" }), _jsx("option", { value: "high", children: "High" }), _jsx("option", { value: "critical", children: "Critical" })] }) }), _jsx(FormField, { label: "Description", children: _jsx("textarea", { value: incidentForm.description, onChange: (event) => setIncidentForm({ ...incidentForm, description: event.target.value }), className: "input" }) }), _jsx(FormField, { label: "Reported By", children: _jsx("input", { value: incidentForm.reported_by, onChange: (event) => setIncidentForm({ ...incidentForm, reported_by: event.target.value }), className: "input" }) }), _jsx(SubmitButton, { text: navigator.onLine ? "Submit Incident" : "Queue Incident", onClick: () => handleSubmit(`/support/${schoolId}/incidents`, incidentForm, createIncidentMutation, () => setIncidentForm({
                                    category: "Safety",
                                    severity: "medium",
                                    description: "",
                                    reported_by: "",
                                })) })] }), _jsxs(FormCard, { title: "Adjust Inventory / Expenses", description: "Log stock movements for canteen, labs, or maintenance. Finance reports update instantly.", children: [_jsx(FormField, { label: "Item Name", children: _jsx("input", { value: inventoryForm.item_name, onChange: (event) => setInventoryForm({ ...inventoryForm, item_name: event.target.value }), className: "input" }) }), _jsx(FormField, { label: "Quantity Change", children: _jsx("input", { type: "number", value: inventoryForm.change_quantity, onChange: (event) => setInventoryForm({ ...inventoryForm, change_quantity: Number(event.target.value) }), className: "input" }) }), _jsx(FormField, { label: "Unit (optional)", children: _jsx("input", { value: inventoryForm.unit, onChange: (event) => setInventoryForm({ ...inventoryForm, unit: event.target.value }), className: "input" }) }), _jsx(FormField, { label: "Reason", children: _jsx("textarea", { value: inventoryForm.reason, onChange: (event) => setInventoryForm({ ...inventoryForm, reason: event.target.value }), className: "input" }) }), _jsx(FormField, { label: "Recorded By", children: _jsx("input", { value: inventoryForm.recorded_by, onChange: (event) => setInventoryForm({ ...inventoryForm, recorded_by: event.target.value }), className: "input" }) }), _jsx(SubmitButton, { text: navigator.onLine ? "Record Adjustment" : "Queue Adjustment", onClick: () => handleSubmit(`/support/${schoolId}/inventory/adjust`, inventoryForm, adjustInventoryMutation, () => setInventoryForm({
                                    item_name: "",
                                    change_quantity: 1,
                                    unit: "",
                                    reason: "",
                                    recorded_by: "",
                                })) })] }), _jsxs(FormCard, { title: "Sickbay / Health Visit", description: "Log student visits to the sickbay. Parents can be notified automatically.", children: [_jsx(FormField, { label: "Student Name", children: _jsx("input", { value: healthForm.student_name, onChange: (event) => setHealthForm({ ...healthForm, student_name: event.target.value }), className: "input" }) }), _jsx(FormField, { label: "Grade/Class", children: _jsx("input", { value: healthForm.grade, onChange: (event) => setHealthForm({ ...healthForm, grade: event.target.value }), className: "input" }) }), _jsx(FormField, { label: "Symptoms", children: _jsx("textarea", { value: healthForm.symptoms, onChange: (event) => setHealthForm({ ...healthForm, symptoms: event.target.value }), className: "input" }) }), _jsx(FormField, { label: "Action Taken", children: _jsx("textarea", { value: healthForm.action_taken, onChange: (event) => setHealthForm({ ...healthForm, action_taken: event.target.value }), className: "input" }) }), _jsx(FormField, { label: "Guardian Contacted (optional)", children: _jsx("input", { value: healthForm.guardian_contacted, onChange: (event) => setHealthForm({ ...healthForm, guardian_contacted: event.target.value }), className: "input" }) }), _jsx(FormField, { label: "Recorded By", children: _jsx("input", { value: healthForm.recorded_by, onChange: (event) => setHealthForm({ ...healthForm, recorded_by: event.target.value }), className: "input" }) }), _jsx(SubmitButton, { text: navigator.onLine ? "Save Health Visit" : "Queue Health Visit", onClick: () => handleSubmit(`/support/${schoolId}/health`, healthForm, recordHealthMutation, () => setHealthForm({
                                    student_name: "",
                                    grade: "",
                                    symptoms: "",
                                    action_taken: "",
                                    guardian_contacted: "",
                                    recorded_by: "",
                                })) })] }), _jsxs(FormCard, { title: "Library Check-in/out", description: "Snap a quick record when books are borrowed or returned. Inventory stays up to date.", children: [_jsx(FormField, { label: "Student Name", children: _jsx("input", { value: libraryForm.student_name, onChange: (event) => setLibraryForm({ ...libraryForm, student_name: event.target.value }), className: "input" }) }), _jsx(FormField, { label: "Class", children: _jsx("input", { value: libraryForm.class_name, onChange: (event) => setLibraryForm({ ...libraryForm, class_name: event.target.value }), className: "input" }) }), _jsx(FormField, { label: "Book Title", children: _jsx("input", { value: libraryForm.book_title, onChange: (event) => setLibraryForm({ ...libraryForm, book_title: event.target.value }), className: "input" }) }), _jsx(FormField, { label: "Action", children: _jsxs("select", { value: libraryForm.action, onChange: (event) => setLibraryForm({ ...libraryForm, action: event.target.value }), className: "input", children: [_jsx("option", { value: "borrow", children: "Borrow" }), _jsx("option", { value: "return", children: "Return" })] }) }), _jsx(FormField, { label: "Due Date (optional)", children: _jsx("input", { type: "date", value: libraryForm.due_date, onChange: (event) => setLibraryForm({ ...libraryForm, due_date: event.target.value }), className: "input" }) }), _jsx(FormField, { label: "Recorded By", children: _jsx("input", { value: libraryForm.recorded_by, onChange: (event) => setLibraryForm({ ...libraryForm, recorded_by: event.target.value }), className: "input" }) }), _jsx(SubmitButton, { text: navigator.onLine ? "Record Transaction" : "Queue Transaction", onClick: () => handleSubmit(`/support/${schoolId}/library`, libraryForm, recordLibraryMutation, () => setLibraryForm({
                                    student_name: "",
                                    class_name: "",
                                    book_title: "",
                                    action: "borrow",
                                    due_date: "",
                                    recorded_by: "",
                                })) })] }), _jsxs(FormCard, { title: "Transport Event", description: "Track school transport departures and arrivals for parents and leadership.", children: [_jsx(FormField, { label: "Route Name", children: _jsx("input", { value: transportForm.route_name, onChange: (event) => setTransportForm({ ...transportForm, route_name: event.target.value }), className: "input" }) }), _jsx(FormField, { label: "Vehicle (optional)", children: _jsx("input", { value: transportForm.vehicle, onChange: (event) => setTransportForm({ ...transportForm, vehicle: event.target.value }), className: "input" }) }), _jsx(FormField, { label: "Status", children: _jsxs("select", { value: transportForm.status, onChange: (event) => setTransportForm({ ...transportForm, status: event.target.value }), className: "input", children: [_jsx("option", { value: "departed", children: "Departed" }), _jsx("option", { value: "arrived", children: "Arrived" }), _jsx("option", { value: "delayed", children: "Delayed" }), _jsx("option", { value: "cancelled", children: "Cancelled" })] }) }), _jsx(FormField, { label: "Notes (optional)", children: _jsx("textarea", { value: transportForm.notes, onChange: (event) => setTransportForm({ ...transportForm, notes: event.target.value }), className: "input" }) }), _jsx(FormField, { label: "Recorded By", children: _jsx("input", { value: transportForm.recorded_by, onChange: (event) => setTransportForm({ ...transportForm, recorded_by: event.target.value }), className: "input" }) }), _jsx(SubmitButton, { text: navigator.onLine ? "Record Transport Event" : "Queue Transport Event", onClick: () => handleSubmit(`/support/${schoolId}/transport`, transportForm, recordTransportMutation, () => setTransportForm({
                                    route_name: "",
                                    vehicle: "",
                                    status: "departed",
                                    notes: "",
                                    recorded_by: "",
                                })) })] })] }), _jsxs("div", { className: "rounded-3xl border border-slate-800 bg-slate-900/60 p-6 space-y-4", children: [_jsx("h2", { className: "text-lg font-semibold", children: "Offline Queue Status" }), _jsx("p", { className: "text-sm text-slate-300", children: "Everything you queue offline appears below. The moment you reconnect, it auto-syncs and leadership receives the report." }), pendingTasks.length === 0 ? (_jsx("p", { className: "text-xs text-slate-500", children: "No queued tasks. You are fully synced." })) : (_jsx("ul", { className: "space-y-2 text-xs text-slate-200", children: pendingTasks.map((task) => (_jsxs("li", { children: ["\u2022 ", task.endpoint, " \u2014 queued at ", new Date(task.createdAt).toLocaleTimeString()] }, task.id))) }))] }), _jsxs("section", { className: "grid gap-6 md:grid-cols-2", children: [_jsx(LogCard, { title: "Recent Incidents", items: incidentsQuery.data ?? [], render: (incident) => (_jsxs("div", { children: [_jsx("p", { className: "font-semibold text-sm", children: incident.category }), _jsx("p", { className: "text-xs text-slate-400", children: incident.description }), _jsxs("p", { className: "text-[11px] uppercase text-slate-500 mt-1", children: ["Severity: ", incident.severity, " \u2022 Status: ", incident.status] })] })) }), _jsx(LogCard, { title: "Inventory Snapshot", items: (inventoryQuery.data?.items ?? []).slice(0, 8), render: (item) => (_jsxs("div", { className: "flex justify-between text-sm", children: [_jsx("span", { children: item.item_name }), _jsxs("span", { className: "font-semibold", children: [item.current_quantity, " ", item.unit ?? ""] })] })) }), _jsx(LogCard, { title: "Sickbay Visits", items: healthQuery.data ?? [], render: (visit) => (_jsxs("div", { children: [_jsx("p", { className: "font-semibold text-sm", children: visit.student_name }), _jsx("p", { className: "text-xs text-slate-400", children: visit.symptoms }), _jsxs("p", { className: "text-[11px] uppercase text-slate-500 mt-1", children: ["Action: ", visit.action_taken] })] })) }), _jsx(LogCard, { title: "Transport Timeline", items: transportQuery.data ?? [], render: (event) => (_jsxs("div", { children: [_jsx("p", { className: "font-semibold text-sm", children: event.route_name }), _jsx("p", { className: "text-xs text-slate-400", children: event.status }), _jsxs("p", { className: "text-[11px] uppercase text-slate-500 mt-1", children: ["Vehicle: ", event.vehicle ?? "N/A"] })] })) }), _jsx(LogCard, { title: "Library Activity", items: libraryQuery.data ?? [], render: (entry) => (_jsxs("div", { children: [_jsx("p", { className: "font-semibold text-sm", children: entry.book_title }), _jsxs("p", { className: "text-xs text-slate-400", children: [entry.student_name, " \u2022 ", entry.action] })] })) })] }), _jsxs("section", { className: "rounded-3xl border border-slate-800 bg-slate-900/60 p-6 space-y-2", children: [_jsx("h2", { className: "text-lg font-semibold", children: "Clarity Support Intelligence" }), reportQuery.isPending ? (_jsx("p", { className: "text-sm text-slate-400", children: "Generating report\u2026" })) : reportQuery.data ? (_jsxs(_Fragment, { children: [_jsx("p", { className: "text-sm text-slate-200", children: reportQuery.data.analysis?.analysis?.summary ??
                                    reportQuery.data.analysis?.summary ??
                                    reportQuery.data.analysis?.analysis ??
                                    "Report ready." }), _jsxs("p", { className: "text-xs text-slate-500", children: ["Generated at ", new Date(reportQuery.data.generated_at).toLocaleString()] })] })) : (_jsx("p", { className: "text-sm text-slate-400", children: "No report yet. Capture a few records and we\u2019ll assemble the briefing automatically." }))] })] }));
};
const FormCard = ({ title, description, children, }) => (_jsxs("div", { className: "rounded-3xl border border-slate-800 bg-slate-900/60 p-6 space-y-4", children: [_jsxs("header", { children: [_jsx("h2", { className: "text-lg font-semibold", children: title }), _jsx("p", { className: "text-xs text-slate-400", children: description })] }), _jsx("div", { className: "space-y-3", children: children })] }));
const FormField = ({ label, children, }) => (_jsxs("label", { className: "flex flex-col gap-1 text-sm", children: [_jsx("span", { className: "text-xs uppercase tracking-wide text-slate-400", children: label }), children] }));
const SubmitButton = ({ text, onClick }) => (_jsx("button", { onClick: onClick, className: "rounded-full bg-emerald-500 px-4 py-2 text-sm font-semibold text-black hover:bg-emerald-400", children: text }));
const LogCard = ({ title, items, render, }) => (_jsxs("div", { className: "rounded-3xl border border-slate-800 bg-slate-900/60 p-5 space-y-3", children: [_jsx("h3", { className: "text-sm font-semibold uppercase tracking-wide text-slate-400", children: title }), items.length === 0 ? (_jsx("p", { className: "text-xs text-slate-500", children: "No entries yet." })) : (_jsx("div", { className: "space-y-2 text-sm text-slate-200", children: items.map((item, idx) => (_jsx("div", { className: "rounded-2xl border border-slate-800/60 bg-slate-950/50 p-3", children: render(item) }, idx))) }))] }));
