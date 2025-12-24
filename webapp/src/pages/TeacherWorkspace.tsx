/**
 * PRODUCTION Teacher Workspace - Complete PWA for Teachers
 * - Real camera integration for photo uploads
 * - Real notifications display
 * - AI chatbot for teachers
 * - Offline-first with background sync
 * - Installable on any device
 */
import { useState, useRef, useEffect } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import dayjs from "dayjs";
import { v4 as uuid } from "uuid";

import { useOfflineSync } from "../hooks/useOfflineSync";
import { useBrandingStore } from "../stores/branding";
import { apiClient } from "../lib/apiClient";

interface Notification {
  id: string;
  title: string;
  message: string;
  type: string;
  created_at: string;
  is_read: boolean;
}

export const TeacherWorkspace = () => {
  const { enqueueTask, tasks } = useOfflineSync();
  const schoolId = useBrandingStore((state) => state.schoolId);
  const teacherId = localStorage.getItem("teacher_id") || "demo-teacher";

  const [activeTab, setActiveTab] = useState<"upload" | "notifications" | "chat" | "dashboard">("upload");
  const [uploadType, setUploadType] = useState<"attendance" | "results" | "sickbay">("attendance");
  const [selectedClass, setSelectedClass] = useState("Primary 5");
  const [selectedSubject, setSelectedSubject] = useState("Mathematics");
  const [capturedPhoto, setCapturedPhoto] = useState<string | null>(null);
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);
  const [chatMessages, setChatMessages] = useState<Array<{ role: string; content: string }>>([]);
  const [chatInput, setChatInput] = useState("");

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
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
  const { data: notifications, refetch: refetchNotifications } = useQuery<Notification[]>({
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
    } catch (error) {
      console.error("Camera error:", error);
      setUploadStatus("Camera not available - use file upload instead");
    }
  };

  // Stop camera
  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = (videoRef.current.srcObject as MediaStream).getTracks();
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
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setCapturedPhoto(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: async () => {
      if (!capturedPhoto) throw new Error("No photo captured");

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
      } else if (uploadType === "results") {
        endpoint = `/teachers/${schoolId}/results/photo`;
      } else {
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
    onError: (error: any) => {
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
      enqueueTask(
        `/teachers/${schoolId}/${uploadType}/photo`,
        {
          photo: capturedPhoto,
          class_name: selectedClass,
          teacher_id: teacherId,
          date_str: dayjs().format("YYYY-MM-DD"),
          ...(uploadType === "results" && { subject: selectedSubject }),
        },
        "POST"
      );
      setUploadStatus("📤 Queued for upload when you reconnect");
      setCapturedPhoto(null);
      return;
    }

    uploadMutation.mutate();
  };

  // Send chat message
  const handleSendChat = async () => {
    if (!chatInput.trim()) return;

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
    } catch (error) {
      setChatMessages((prev) => [...prev, { role: "assistant", content: "I'll answer when we reconnect." }]);
    }
  };

  const pendingCount = tasks.length;
  const unreadNotifications = notifications?.filter((n) => !n.is_read).length || 0;

  return (
    <section className="space-y-6 p-4">
      {/* Header */}
      <header className="space-y-2">
        <h1 className="text-3xl font-bold">Teacher Workspace</h1>
        <p className="text-slate-300">
          📸 Snap photos of attendance, results, or sickbay registers - AI does the rest.
          All notifications in-app. Zero WhatsApp/SMS costs.
        </p>
      </header>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-slate-700">
        {["upload", "notifications", "chat", "dashboard"].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab as any)}
            className={`px-4 py-2 font-semibold capitalize ${activeTab === tab
                ? "border-b-2 border-blue-500 text-blue-500"
                : "text-slate-400 hover:text-slate-200"
              }`}
          >
            {tab}
            {tab === "notifications" && unreadNotifications > 0 && (
              <span className="ml-2 rounded-full bg-red-500 px-2 py-0.5 text-xs text-white">
                {unreadNotifications}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Photo Upload Tab */}
      {activeTab === "upload" && (
        <div className="space-y-6">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
            <h2 className="text-xl font-semibold">📸 Photo Upload</h2>

            <div className="grid gap-4 md:grid-cols-3">
              <div>
                <label className="text-sm font-medium">Upload Type</label>
                <select
                  value={uploadType}
                  onChange={(e) => setUploadType(e.target.value as any)}
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 mt-1"
                >
                  <option value="attendance">Attendance Sheet</option>
                  <option value="results">Exam Results</option>
                  <option value="sickbay">Sickbay Register</option>
                  <option value="passport">Passport Photo</option>
                </select>
              </div>

              <div>
                <label className="text-sm font-medium">Class</label>
                <select
                  value={selectedClass}
                  onChange={(e) => setSelectedClass(e.target.value)}
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 mt-1"
                >
                  <option>Primary 5</option>
                  <option>Primary 6</option>
                  <option>Primary 7</option>
                  <option>Secondary 1</option>
                </select>
              </div>

              {uploadType === "results" && (
                <div>
                  <label className="text-sm font-medium">Subject</label>
                  <select
                    value={selectedSubject}
                    onChange={(e) => setSelectedSubject(e.target.value)}
                    className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 mt-1"
                  >
                    <option>Mathematics</option>
                    <option>English</option>
                    <option>Science</option>
                    <option>Social Studies</option>
                  </select>
                </div>
              )}
            </div>

            {!capturedPhoto && (
              <div className="space-y-4">
                <div className="flex gap-4">
                  <button
                    onClick={cameraActive ? stopCamera : startCamera}
                    className="rounded-lg bg-blue-600 px-6 py-3 font-semibold hover:bg-blue-500"
                  >
                    {cameraActive ? "📷 Stop Camera" : "📷 Use Camera"}
                  </button>
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="rounded-lg bg-slate-700 px-6 py-3 font-semibold hover:bg-slate-600"
                  >
                    📁 Upload File
                  </button>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                </div>

                {cameraActive && (
                  <div className="space-y-4">
                    <video
                      ref={videoRef}
                      autoPlay
                      playsInline
                      className="w-full max-w-2xl rounded-lg border border-slate-700"
                    />
                    <button
                      onClick={capturePhoto}
                      className="rounded-lg bg-green-600 px-6 py-3 font-semibold hover:bg-green-500"
                    >
                      📸 Capture Photo
                    </button>
                  </div>
                )}
                <canvas ref={canvasRef} className="hidden" />
              </div>
            )}

            {capturedPhoto && (
              <div className="space-y-4">
                <img src={capturedPhoto} alt="Captured" className="max-w-2xl rounded-lg border border-slate-700" />
                <div className="flex gap-4">
                  <button
                    onClick={handleUpload}
                    disabled={uploadMutation.isPending}
                    className="rounded-lg bg-green-600 px-6 py-3 font-semibold hover:bg-green-500 disabled:opacity-50"
                  >
                    {uploadMutation.isPending ? "⏳ Processing..." : "✅ Upload & Process"}
                  </button>
                  <button
                    onClick={() => setCapturedPhoto(null)}
                    className="rounded-lg bg-red-600 px-6 py-3 font-semibold hover:bg-red-500"
                  >
                    🗑️ Discard
                  </button>
                </div>
              </div>
            )}

            {uploadStatus && (
              <div className={`rounded-lg border p-4 ${uploadStatus.includes("Success")
                  ? "border-green-500 bg-green-500/10 text-green-100"
                  : uploadStatus.includes("Error")
                    ? "border-red-500 bg-red-500/10 text-red-100"
                    : "border-blue-500 bg-blue-500/10 text-blue-100"
                }`}>
                {uploadStatus}
              </div>
            )}
          </div>

          {pendingCount > 0 && (
            <div className="rounded-2xl border border-amber-500 bg-amber-500/10 p-4">
              <p className="font-semibold">📤 {pendingCount} uploads queued for when you reconnect</p>
            </div>
          )}
        </div>
      )}

      {/* Notifications Tab */}
      {activeTab === "notifications" && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">🔔 Notifications</h2>

          {!notifications || notifications.length === 0 ? (
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-8 text-center text-slate-400">
              No notifications yet. They'll appear here when parents message you or system events occur.
            </div>
          ) : (
            <div className="space-y-3">
              {notifications.map((notif) => (
                <div
                  key={notif.id}
                  className={`rounded-2xl border p-4 ${notif.is_read
                      ? "border-slate-800 bg-slate-900/40"
                      : "border-blue-500 bg-blue-500/10"
                    }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold">{notif.title}</h3>
                      <p className="mt-1 text-sm text-slate-300">{notif.message}</p>
                      <p className="mt-2 text-xs text-slate-400">
                        {dayjs(notif.created_at).fromNow()}
                      </p>
                    </div>
                    {!notif.is_read && (
                      <span className="rounded-full bg-blue-500 px-2 py-1 text-xs font-semibold">
                        NEW
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Chat Tab */}
      {activeTab === "chat" && (
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
          <h2 className="text-xl font-semibold">💬 AI Assistant</h2>
          <p className="text-sm text-slate-300">
            Ask the AI to generate reports, analyze data, or get teaching recommendations.
          </p>

          <div className="h-96 overflow-y-auto space-y-3 rounded-lg bg-slate-950/60 p-4">
            {chatMessages.length === 0 && (
              <p className="text-sm text-slate-400">
                Try: "Generate class performance report for Primary 5"
              </p>
            )}
            {chatMessages.map((msg, idx) => (
              <div
                key={idx}
                className={`max-w-sm rounded-lg p-3 ${msg.role === "user"
                    ? "ml-auto bg-blue-600 text-white"
                    : "bg-slate-800 text-slate-200"
                  }`}
              >
                {msg.content}
              </div>
            ))}
          </div>

          <div className="flex gap-2">
            <input
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleSendChat()}
              placeholder="Ask the AI assistant..."
              className="flex-1 rounded-lg border border-slate-700 bg-slate-950 px-4 py-2"
            />
            <button
              onClick={handleSendChat}
              className="rounded-lg bg-blue-600 px-6 py-2 font-semibold hover:bg-blue-500"
            >
              Send
            </button>
          </div>
        </div>
      )}

      {/* Dashboard Tab */}
      {activeTab === "dashboard" && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">📊 My Dashboard</h2>

          <div className="grid gap-4 md:grid-cols-3">
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
              <p className="text-sm text-slate-400">Students</p>
              <p className="text-3xl font-bold mt-2">{dashboard?.total_students || 0}</p>
            </div>
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
              <p className="text-sm text-slate-400">Classes</p>
              <p className="text-3xl font-bold mt-2">{dashboard?.classes?.length || 0}</p>
            </div>
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
              <p className="text-sm text-slate-400">Marked Today</p>
              <p className="text-3xl font-bold mt-2">{dashboard?.attendance_today?.total_marked || 0}</p>
            </div>
          </div>

          {dashboard?.quick_actions && (
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
              <h3 className="font-semibold mb-4">Quick Actions</h3>
              <div className="grid gap-3 md:grid-cols-2">
                {dashboard.quick_actions.map((action: any) => (
                  <button
                    key={action.id}
                    className="rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-left hover:bg-slate-800"
                  >
                    <span className="mr-2">{action.icon}</span>
                    {action.label}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </section>
  );
};
