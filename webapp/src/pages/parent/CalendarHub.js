import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { Calendar, momentLocalizer } from 'react-big-calendar';
import moment from 'moment';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import { Calendar as CalIcon, Bell, CheckCircle, Clock } from 'lucide-react';
const localizer = momentLocalizer(moment);
const CalendarHub = () => {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);
    useEffect(() => {
        // Mock fetching events from the API
        const fetchEvents = async () => {
            setLoading(true);
            // In a real app: fetch(`/api/events/upcoming`)
            setTimeout(() => {
                setEvents([
                    {
                        id: 1,
                        title: 'P.3 Sports Day',
                        start: new Date(2025, 11, 28, 10, 0),
                        end: new Date(2025, 11, 28, 16, 0),
                        type: 'sports',
                        synced: true
                    },
                    {
                        id: 2,
                        title: 'PTA General Meeting',
                        start: new Date(2025, 11, 30, 14, 0),
                        end: new Date(2025, 11, 30, 17, 0),
                        type: 'meeting',
                        synced: true
                    }
                ]);
                setLoading(false);
            }, 800);
        };
        fetchEvents();
    }, []);
    return (_jsxs("div", { className: "p-4 bg-gray-50 min-h-screen", children: [_jsxs("header", { className: "flex justify-between items-center mb-6", children: [_jsxs("div", { children: [_jsxs("h1", { className: "text-2xl font-bold text-gray-800 flex items-center gap-2", children: [_jsx(CalIcon, { className: "text-blue-600" }), " School Calendar"] }), _jsx("p", { className: "text-gray-500 text-sm", children: "Automatically synced with your Google Calendar" })] }), _jsxs("button", { className: "p-2 bg-white rounded-full shadow-sm relative", children: [_jsx(Bell, { className: "w-6 h-6 text-gray-600" }), _jsx("span", { className: "absolute top-0 right-0 w-3 h-3 bg-red-500 border-2 border-white rounded-full" })] })] }), _jsx("div", { className: "bg-white rounded-2xl shadow-xl p-4 mb-6", style: { height: '500px' }, children: _jsx(Calendar, { localizer: localizer, events: events, startAccessor: "start", endAccessor: "end", style: { height: '100%' }, eventPropGetter: (event) => ({
                        className: `rounded-lg border-l-4 ${event.type === 'sports' ? 'bg-orange-50 border-orange-500 text-orange-700' :
                            'bg-blue-50 border-blue-500 text-blue-700'}`
                    }) }) }), _jsxs("section", { children: [_jsx("h2", { className: "text-lg font-semibold mb-4 text-gray-700", children: "Automation Status" }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 gap-4", children: [_jsxs("div", { className: "bg-white p-4 rounded-xl border border-gray-100 flex items-center gap-4", children: [_jsx("div", { className: "p-3 bg-green-50 rounded-lg", children: _jsx(CheckCircle, { className: "text-green-500" }) }), _jsxs("div", { children: [_jsx("h3", { className: "font-medium", children: "Google Sync Active" }), _jsx("p", { className: "text-xs text-gray-500", children: "Events are auto-blocked in your calendar." })] })] }), _jsxs("div", { className: "bg-white p-4 rounded-xl border border-gray-100 flex items-center gap-4", children: [_jsx("div", { className: "p-3 bg-blue-50 rounded-lg", children: _jsx(Clock, { className: "text-blue-500" }) }), _jsxs("div", { children: [_jsx("h3", { className: "font-medium", children: "Notification Loop" }), _jsx("p", { className: "text-xs text-gray-500", children: "Scheduled: 7-day, 3-day, and 1-day alerts." })] })] })] })] })] }));
};
export default CalendarHub;
