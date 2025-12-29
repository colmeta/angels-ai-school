/**
 * Attendance Service
 * Handles Subject and Exam attendance recording
 * Orchestrates: Input -> AI Worker (Parsing) -> Local DB (Sync) -> API (Backend)
 */
import { supabase } from '../lib/supabase';

export interface AttendanceInput {
    type: 'subject' | 'exam';
    inputType: 'photo' | 'voice' | 'text' | 'manual';
    data: any; // Image file, text string, or manual records
    metadata: {
        student_id?: string; // For syncing context
        class_name: string;
        subject: string;
        exam_name?: string;
        date?: string;
    };
}

class AttendanceService {
    private worker: Worker;

    constructor() {
        this.worker = new Worker(new URL('../workers/aiWorker.ts', import.meta.url), {
            type: 'module'
        });
    }

    /**
     * Process attendance input (Photo, Voice, Text)
     * Returns structured records ready for confirmation
     */
    async processAttendance(input: AttendanceInput): Promise<any> {
        return new Promise((resolve, reject) => {

            // Set up one-time listener for result
            const handler = (e: MessageEvent) => {
                const { type, data } = e.data;

                if (type === 'PARSE_RESULT') {
                    this.worker.removeEventListener('message', handler);
                    resolve(data);
                } else if (type === 'ERROR') {
                    this.worker.removeEventListener('message', handler);
                    reject(data);
                }
            };

            this.worker.addEventListener('message', handler);

            // Send command to worker
            if (input.inputType === 'photo') {
                // Convert file to base64 if needed, or pass File object
                this.worker.postMessage({
                    type: 'PROCESS_ATTENDANCE_IMAGE',
                    data: {
                        image: input.data,
                        context: input.metadata
                    }
                });
            } else if (input.inputType === 'text' || input.inputType === 'voice') {
                this.worker.postMessage({
                    type: 'PARSE_ATTENDANCE_TEXT',
                    data: {
                        text: input.data,
                        context: input.metadata
                    }
                });
            } else {
                // Manual - no parsing needed
                resolve(input.data);
            }
        });
    }

    /**
     * Submit confirmed records to backend
     */
    async submitBatch(type: 'subject' | 'exam', records: any[]) {
        try {
            const { data, error } = await supabase.auth.getSession();
            const token = data.session?.access_token;

            const response = await fetch(`${import.meta.env.VITE_API_URL}/api/attendance/batch`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    type,
                    records
                })
            });

            if (!response.ok) {
                throw new Error('Failed to submit attendance');
            }

            return await response.json();

        } catch (error) {
            console.error('Submission failed:', error);
            // TODO: Queue for offline sync
            throw error;
        }
    }
}

export const attendanceService = new AttendanceService();
