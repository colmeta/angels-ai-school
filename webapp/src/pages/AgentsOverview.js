import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
const agents = [
    {
        name: "Angels AI Digital CEO",
        mission: "Delivers strategic briefings, growth playbooks, and executive decisions using Clarity’s intelligence.",
    },
    {
        name: "Command Intelligence Agent – Clarity Engine",
        mission: "Turns natural language commands into precise workflows, coordinating all other agents.",
    },
    {
        name: "Document Intelligence Agent – RAG Master",
        mission: "Digitizes handwritten forms, routes data to the right systems, and builds searchable knowledge bases.",
    },
    {
        name: "Parent Engagement Agent – The Oracle",
        mission: "Provides 24/7 multilingual parent support and proactive communications.",
    },
    {
        name: "Financial Operations Agent – Automated Treasurer",
        mission: "Runs fee collection OODA loops, mobile money reconciliation, and compliance reporting.",
    },
    {
        name: "Academic Operations Agent – Educational Excellence Manager",
        mission: "Generates learning insights, predicts at-risk students, and optimizes curriculum delivery.",
    },
    {
        name: "Teacher Liberation Agent – Administrative Freedom Fighter",
        mission: "Automates non-teaching tasks so teachers focus purely on learners.",
    },
    {
        name: "Executive Assistant Agent – Ultimate Administrative Coordinator",
        mission: "Schedules, drafts, and prepares board-ready reports with zero manual effort.",
    },
    {
        name: "Security & Safety Guardian",
        mission: "Manages visitor logs, incidents, and emergency alerts to protect every child.",
    },
];
export const AgentsOverview = () => (_jsxs("section", { className: "space-y-6", children: [_jsxs("header", { className: "space-y-2", children: [_jsx("h1", { className: "text-2xl font-semibold", children: "Meet the Angels AI Crew" }), _jsx("p", { className: "text-slate-300", children: "Nine specialized agents working together with the Clarity engine to deliver a full-stack school operations Ferrari." })] }), _jsx("div", { className: "grid gap-4 lg:grid-cols-3", children: agents.map((agent) => (_jsxs("article", { className: "rounded-3xl border border-slate-800 bg-slate-900/60 p-6 space-y-2", children: [_jsx("h2", { className: "text-lg font-semibold", children: agent.name }), _jsx("p", { className: "text-sm text-slate-300", children: agent.mission })] }, agent.name))) })] }));
