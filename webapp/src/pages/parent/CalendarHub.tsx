import React, { useState, useEffect } from 'react';
import { Calendar, momentLocalizer } from 'react-big-calendar';
import moment from 'moment';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import { Calendar as CalIcon, Bell, CheckCircle, Clock } from 'lucide-react';

const localizer = momentLocalizer(moment);

interface CalendarEvent {
    id: number;
    title: string;
    start: Date;
    end: Date;
    type: string;
    synced: boolean;
}

const CalendarHub: React.FC = () => {
    const [events, setEvents] = useState<CalendarEvent[]>([]);
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

    return (
        <div className="p-4 bg-gray-50 min-h-screen">
            <header className="flex justify-between items-center mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
                        <CalIcon className="text-blue-600" /> School Calendar
                    </h1>
                    <p className="text-gray-500 text-sm">Automatically synced with your Google Calendar</p>
                </div>
                <button className="p-2 bg-white rounded-full shadow-sm relative">
                    <Bell className="w-6 h-6 text-gray-600" />
                    <span className="absolute top-0 right-0 w-3 h-3 bg-red-500 border-2 border-white rounded-full"></span>
                </button>
            </header>

            <div className="bg-white rounded-2xl shadow-xl p-4 mb-6" style={{ height: '500px' }}>
                <Calendar
                    localizer={localizer}
                    events={events}
                    startAccessor="start"
                    endAccessor="end"
                    style={{ height: '100%' }}
                    eventPropGetter={(event) => ({
                        className: `rounded-lg border-l-4 ${event.type === 'sports' ? 'bg-orange-50 border-orange-500 text-orange-700' :
                            'bg-blue-50 border-blue-500 text-blue-700'
                            }`
                    })}
                />
            </div>

            <section>
                <h2 className="text-lg font-semibold mb-4 text-gray-700">Automation Status</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-white p-4 rounded-xl border border-gray-100 flex items-center gap-4">
                        <div className="p-3 bg-green-50 rounded-lg">
                            <CheckCircle className="text-green-500" />
                        </div>
                        <div>
                            <h3 className="font-medium">Google Sync Active</h3>
                            <p className="text-xs text-gray-500">Events are auto-blocked in your calendar.</p>
                        </div>
                    </div>
                    <div className="bg-white p-4 rounded-xl border border-gray-100 flex items-center gap-4">
                        <div className="p-3 bg-blue-50 rounded-lg">
                            <Clock className="text-blue-500" />
                        </div>
                        <div>
                            <h3 className="font-medium">Notification Loop</h3>
                            <p className="text-xs text-gray-500">Scheduled: 7-day, 3-day, and 1-day alerts.</p>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
};

export default CalendarHub;
