import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * PRODUCTION Teacher Workspace - Complete PWA for Teachers
 * - Real camera integration for photo uploads
 * - Real notifications display
 * - AI chatbot for teachers
 * - Offline-first with background sync
 * - Installable on any device
 */
import { useState, useRef } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import dayjs from "dayjs";
import { useOfflineSync } from "../hooks/useOfflineSync";
import { useBrandingStore } from "../stores/branding";
import { apiClient } from "../lib/apiClient";
export const TeacherWorkspace = () => {
    const { enqueueTask, tasks } = useOfflineSync();
    const schoolId = useBrandingStore((state) => state.schoolId);
    const teacherId = localStorage.getItem("teacher_id") || "demo-teacher";
    const [activeTab, setActiveTab] = useState("upload");
    const [uploadType, setUploadType] = useState("attendance");
    const [selectedClass, setSelectedClass] = useState("Primary 5");
    const [selectedSubject, setSelectedSubject] = useState("Mathematics");
    const [capturedPhoto, setCapturedPhoto] = useState(null);
    const [uploadStatus, setUploadStatus] = useState(null);
    const [chatMessages, setChatMessages] = useState([]);
    const [chatInput, setChatInput] = useState("");
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const fileInputRef = useRef(null);
    const [cameraActive, setCameraActive] = useState(false);
    // Fetch teacher dashboard data
    const { data: dashboard } = useQuery({
        queryKey: ["teacher-dashboard", schoolId, teacherId],
        queryFn: async () => {
            const res = await apiClient.get(`/teachers/${schoolId}/teacher/${teacherId}/dashboard`);
            return res.data;
        },
        enabled: Boolean(schoolId && teacherId) && navigator.onLine,
    });
    // Fetch notifications
    const { data: notifications, refetch: refetchNotifications } = useQuery({
        queryKey: ["teacher-notifications", teacherId],
        queryFn: async () => {
            const res = await apiClient.get(`/notifications/teacher/${teacherId}`);
            return res.data.notifications || [];
        },
        enabled: Boolean(teacherId) && navigator.onLine,
    });
    // Start camera
    const startCamera = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: "environment" },
                audio: false
            });
            if (videoRef.current) {
                videoRef.current.srcObject = stream;
                setCameraActive(true);
            }
        }
        catch (error) {
            console.error("Camera error:", error);
            setUploadStatus("Camera not available - use file upload instead");
        }
    };
    // Stop camera
    const stopCamera = () => {
        if (videoRef.current && videoRef.current.srcObject) {
            const tracks = videoRef.current.srcObject.getTracks();
            tracks.forEach(track => track.stop());
            setCameraActive(false);
        }
    };
    // Capture photo from camera
    const capturePhoto = () => {
        if (videoRef.current && canvasRef.current) {
            const context = canvasRef.current.getContext("2d");
            if (context) {
                canvasRef.current.width = videoRef.current.videoWidth;
                canvasRef.current.height = videoRef.current.videoHeight;
                context.drawImage(videoRef.current, 0, 0);
                const photoData = canvasRef.current.toDataURL("image/jpeg");
                setCapturedPhoto(photoData);
                stopCamera();
            }
        }
    };
    // Handle file upload
    const handleFileUpload = (event) => {
        const file = event.target.files?.[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                setCapturedPhoto(e.target?.result);
            };
            reader.readAsDataURL(file);
        }
    };
    // Upload mutation
    const uploadMutation = useMutation({
        mutationFn: async () => {
            if (!capturedPhoto)
                throw new Error("No photo captured");
            const formData = new FormData();
            // Convert base64 to blob
            const blob = await (await fetch(capturedPhoto)).blob();
            formData.append("photo", blob, "capture.jpg");
            formData.append("school_id", schoolId || "");
            formData.append("teacher_id", teacherId);
            formData.append("class_name", selectedClass);
            formData.append("date_str", dayjs().format("YYYY-MM-DD"));
            if (uploadType === "results") {
                formData.append("subject", selectedSubject);
                formData.append("exam_name", "Recent Assessment");
                formData.append("max_marks", "100");
            }
            let endpoint = "";
            if (uploadType === "attendance") {
                endpoint = `/teachers/${schoolId}/attendance/photo`;
            }
            else if (uploadType === "results") {
                endpoint = `/teachers/${schoolId}/results/photo`;
            }
            else {
                endpoint = `/teachers/${schoolId}/sickbay/photo`;
            }
            const res = await apiClient.post(endpoint, formData, {
                headers: { "Content-Type": "multipart/form-data" },
            });
            return res.data;
        },
        onSuccess: (data) => {
            setUploadStatus(`✅ Success! ${data.records_saved || data.results_saved || data.visits_recorded} records processed. ${data.parents_notified || 0} parents notified.`);
            setCapturedPhoto(null);
            refetchNotifications();
        },
        onError: (error) => {
            setUploadStatus(`❌ Error: ${error.response?.data?.detail || error.message}`);
        },
    });
    // Handle upload
    const handleUpload = () => {
        if (!capturedPhoto) {
            setUploadStatus("Please capture or select a photo first");
            return;
        }
        if (!navigator.onLine) {
            // Queue for offline sync
            enqueueTask(`/teachers/${schoolId}/${uploadType}/photo`, {
                photo: capturedPhoto,
                class_name: selectedClass,
                teacher_id: teacherId,
                date_str: dayjs().format("YYYY-MM-DD"),
                ...(uploadType === "results" && { subject: selectedSubject }),
            }, "POST");
            setUploadStatus("📤 Queued for upload when you reconnect");
            setCapturedPhoto(null);
            return;
        }
        uploadMutation.mutate();
    };
    // Send chat message
    const handleSendChat = async () => {
        if (!chatInput.trim())
            return;
        const userMessage = { role: "user", content: chatInput };
        setChatMessages((prev) => [...prev, userMessage]);
        setChatInput("");
        if (!navigator.onLine) {
            setChatMessages((prev) => [...prev, { role: "assistant", content: "I'll answer when you're back online." }]);
            return;
        }
        try {
            const res = await apiClient.post(`/chatbot/query`, {
                school_id: schoolId,
                user_query: chatInput,
                user_type: "teacher",
                user_id: teacherId,
            });
            setChatMessages((prev) => [...prev, { role: "assistant", content: res.data.answer || "I'm here to help!" }]);
        }
        catch (error) {
            setChatMessages((prev) => [...prev, { role: "assistant", content: "I'll answer when we reconnect." }]);
        }
    };
    const pendingCount = tasks.length;
    const unreadNotifications = notifications?.filter((n) => !n.is_read).length || 0;
    return (_jsxs("section", { className: "space-y-6 p-4", children: [_jsxs("header", { className: "space-y-2", children: [_jsx("h1", { className: "text-3xl font-bold", children: "Teacher Workspace" }), _jsx("p", { className: "text-slate-300", children: "\uD83D\uDCF8 Snap photos of attendance, results, or sickbay registers - AI does the rest. All notifications in-app. Zero WhatsApp/SMS costs." })] }), _jsx("div", { className: "flex gap-2 border-b border-slate-700", children: ["upload", "notifications", "chat", "dashboard"].map((tab) => (_jsxs("button", { onClick: () => setActiveTab(tab), className: `px-4 py-2 font-semibold capitalize ${activeTab === tab
                        ? "border-b-2 border-blue-500 text-blue-500"
                        : "text-slate-400 hover:text-slate-200"}`, children: [tab, tab === "notifications" && unreadNotifications > 0 && (_jsx("span", { className: "ml-2 rounded-full bg-red-500 px-2 py-0.5 text-xs text-white", children: unreadNotifications }))] }, tab))) }), activeTab === "upload" && (_jsxs("div", { className: "space-y-6", children: [_jsxs("div", { className: "rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4", children: [_jsx("h2", { className: "text-xl font-semibold", children: "\uD83D\uDCF8 Photo Upload" }), _jsxs("div", { className: "grid gap-4 md:grid-cols-3", children: [_jsxs("div", { children: [_jsx("label", { className: "text-sm font-medium", children: "Upload Type" }), _jsxs("select", { value: uploadType, onChange: (e) => setUploadType(e.target.value), className: "w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 mt-1", children: [_jsx("option", { value: "attendance", children: "Attendance Sheet" }), _jsx("option", { value: "results", children: "Exam Results" }), _jsx("option", { value: "sickbay", children: "Sickbay Register" }), _jsx("option", { value: "passport", children: "Passport Photo" })] })] }), _jsxs("div", { children: [_jsx("label", { className: "text-sm font-medium", children: "Class" }), _jsxs("select", { value: selectedClass, onChange: (e) => setSelectedClass(e.target.value), className: "w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 mt-1", children: [_jsx("option", { children: "Primary 5" }), _jsx("option", { children: "Primary 6" }), _jsx("option", { children: "Primary 7" }), _jsx("option", { children: "Secondary 1" })] })] }), uploadType === "results" && (_jsxs("div", { children: [_jsx("label", { className: "text-sm font-medium", children: "Subject" }), _jsxs("select", { value: selectedSubject, onChange: (e) => setSelectedSubject(e.target.value), className: "w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 mt-1", children: [_jsx("option", { children: "Mathematics" }), _jsx("option", { children: "English" }), _jsx("option", { children: "Science" }), _jsx("option", { children: "Social Studies" })] })] }))] }), !capturedPhoto && (_jsxs("div", { className: "space-y-4", children: [_jsxs("div", { className: "flex gap-4", children: [_jsx("button", { onClick: cameraActive ? stopCamera : startCamera, className: "rounded-lg bg-blue-600 px-6 py-3 font-semibold hover:bg-blue-500", children: cameraActive ? "📷 Stop Camera" : "📷 Use Camera" }), _jsx("button", { onClick: () => fileInputRef.current?.click(), className: "rounded-lg bg-slate-700 px-6 py-3 font-semibold hover:bg-slate-600", children: "\uD83D\uDCC1 Upload File" }), _jsx("input", { ref: fileInputRef, type: "file", accept: "image/*", onChange: handleFileUpload, className: "hidden" })] }), cameraActive && (_jsxs("div", { className: "space-y-4", children: [_jsx("video", { ref: videoRef, autoPlay: true, playsInline: true, className: "w-full max-w-2xl rounded-lg border border-slate-700" }), _jsx("button", { onClick: capturePhoto, className: "rounded-lg bg-green-600 px-6 py-3 font-semibold hover:bg-green-500", children: "\uD83D\uDCF8 Capture Photo" })] })), _jsx("canvas", { ref: canvasRef, className: "hidden" })] })), capturedPhoto && (_jsxs("div", { className: "space-y-4", children: [_jsx("img", { src: capturedPhoto, alt: "Captured", className: "max-w-2xl rounded-lg border border-slate-700" }), _jsxs("div", { className: "flex gap-4", children: [_jsx("button", { onClick: handleUpload, disabled: uploadMutation.isPending, className: "rounded-lg bg-green-600 px-6 py-3 font-semibold hover:bg-green-500 disabled:opacity-50", children: uploadMutation.isPending ? "⏳ Processing..." : "✅ Upload & Process" }), _jsx("button", { onClick: () => setCapturedPhoto(null), className: "rounded-lg bg-red-600 px-6 py-3 font-semibold hover:bg-red-500", children: "\uD83D\uDDD1\uFE0F Discard" })] })] })), uploadStatus && (_jsx("div", { className: `rounded-lg border p-4 ${uploadStatus.includes("Success")
                                    ? "border-green-500 bg-green-500/10 text-green-100"
                                    : uploadStatus.includes("Error")
                                        ? "border-red-500 bg-red-500/10 text-red-100"
                                        : "border-blue-500 bg-blue-500/10 text-blue-100"}`, children: uploadStatus }))] }), pendingCount > 0 && (_jsx("div", { className: "rounded-2xl border border-amber-500 bg-amber-500/10 p-4", children: _jsxs("p", { className: "font-semibold", children: ["\uD83D\uDCE4 ", pendingCount, " uploads queued for when you reconnect"] }) }))] })), activeTab === "notifications" && (_jsxs("div", { className: "space-y-4", children: [_jsx("h2", { className: "text-xl font-semibold", children: "\uD83D\uDD14 Notifications" }), !notifications || notifications.length === 0 ? (_jsx("div", { className: "rounded-2xl border border-slate-800 bg-slate-900/60 p-8 text-center text-slate-400", children: "No notifications yet. They'll appear here when parents message you or system events occur." })) : (_jsx("div", { className: "space-y-3", children: notifications.map((notif) => (_jsx("div", { className: `rounded-2xl border p-4 ${notif.is_read
                                ? "border-slate-800 bg-slate-900/40"
                                : "border-blue-500 bg-blue-500/10"}`, children: _jsxs("div", { className: "flex items-start justify-between", children: [_jsxs("div", { className: "flex-1", children: [_jsx("h3", { className: "font-semibold", children: notif.title }), _jsx("p", { className: "mt-1 text-sm text-slate-300", children: notif.message }), _jsx("p", { className: "mt-2 text-xs text-slate-400", children: dayjs(notif.created_at).fromNow() })] }), !notif.is_read && (_jsx("span", { className: "rounded-full bg-blue-500 px-2 py-1 text-xs font-semibold", children: "NEW" }))] }) }, notif.id))) }))] })), activeTab === "chat" && (_jsxs("div", { className: "rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4", children: [_jsx("h2", { className: "text-xl font-semibold", children: "\uD83D\uDCAC AI Assistant" }), _jsx("p", { className: "text-sm text-slate-300", children: "Ask the AI to generate reports, analyze data, or get teaching recommendations." }), _jsxs("div", { className: "h-96 overflow-y-auto space-y-3 rounded-lg bg-slate-950/60 p-4", children: [chatMessages.length === 0 && (_jsx("p", { className: "text-sm text-slate-400", children: "Try: \"Generate class performance report for Primary 5\"" })), chatMessages.map((msg, idx) => (_jsx("div", { className: `max-w-sm rounded-lg p-3 ${msg.role === "user"
                                    ? "ml-auto bg-blue-600 text-white"
                                    : "bg-slate-800 text-slate-200"}`, children: msg.content }, idx)))] }), _jsxs("div", { className: "flex gap-2", children: [_jsx("input", { value: chatInput, onChange: (e) => setChatInput(e.target.value), onKeyPress: (e) => e.key === "Enter" && handleSendChat(), placeholder: "Ask the AI assistant...", className: "flex-1 rounded-lg border border-slate-700 bg-slate-950 px-4 py-2" }), _jsx("button", { onClick: handleSendChat, className: "rounded-lg bg-blue-600 px-6 py-2 font-semibold hover:bg-blue-500", children: "Send" })] })] })), activeTab === "dashboard" && (_jsxs("div", { className: "space-y-4", children: [_jsx("h2", { className: "text-xl font-semibold", children: "\uD83D\uDCCA My Dashboard" }), _jsxs("div", { className: "grid gap-4 md:grid-cols-3", children: [_jsxs("div", { className: "rounded-2xl border border-slate-800 bg-slate-900/60 p-6", children: [_jsx("p", { className: "text-sm text-slate-400", children: "Students" }), _jsx("p", { className: "text-3xl font-bold mt-2", children: dashboard?.total_students || 0 })] }), _jsxs("div", { className: "rounded-2xl border border-slate-800 bg-slate-900/60 p-6", children: [_jsx("p", { className: "text-sm text-slate-400", children: "Classes" }), _jsx("p", { className: "text-3xl font-bold mt-2", children: dashboard?.classes?.length || 0 })] }), _jsxs("div", { className: "rounded-2xl border border-slate-800 bg-slate-900/60 p-6", children: [_jsx("p", { className: "text-sm text-slate-400", children: "Marked Today" }), _jsx("p", { className: "text-3xl font-bold mt-2", children: dashboard?.attendance_today?.total_marked || 0 })] })] }), dashboard?.quick_actions && (_jsxs("div", { className: "rounded-2xl border border-slate-800 bg-slate-900/60 p-6", children: [_jsx("h3", { className: "font-semibold mb-4", children: "Quick Actions" }), _jsx("div", { className: "grid gap-3 md:grid-cols-2", children: dashboard.quick_actions.map((action) => (_jsxs("button", { className: "rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-left hover:bg-slate-800", children: [_jsx("span", { className: "mr-2", children: action.icon }), action.label] }, action.id))) })] }))] }))] }));
};
