import React, { Component, ErrorInfo, ReactNode } from "react";
import { AlertTriangle, RefreshCw, Home } from "lucide-react";

interface Props {
    children: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
    errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
    public state: State = {
        hasError: false,
        error: null,
        errorInfo: null,
    };

    public static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error, errorInfo: null };
    }

    public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error("Uncaught error:", error, errorInfo);
        this.setState({ errorInfo });
    }

    private handleReload = () => {
        window.location.reload();
    };

    private handleGoHome = () => {
        window.location.href = "/";
    };

    public render() {
        if (this.state.hasError) {
            return (
                <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4 font-sans text-slate-900">
                    <div className="max-w-md w-full bg-white rounded-2xl shadow-xl border border-slate-200 p-8 text-center">
                        <div className="w-16 h-16 bg-red-100 text-red-600 rounded-full flex items-center justify-center mx-auto mb-6">
                            <AlertTriangle size={32} />
                        </div>

                        <h1 className="text-2xl font-bold mb-2">Something went wrong</h1>
                        <p className="text-slate-500 mb-6">
                            The application encountered an unexpected error.
                        </p>

                        <div className="text-left bg-slate-100 p-4 rounded-lg mb-6 overflow-auto max-h-48 text-xs font-mono text-slate-700 border border-slate-200">
                            <p className="font-bold text-red-600 mb-1">{this.state.error?.toString()}</p>
                            <pre className="whitespace-pre-wrap">{this.state.errorInfo?.componentStack}</pre>
                        </div>

                        <div className="flex gap-3 justify-center">
                            <button
                                onClick={this.handleReload}
                                className="flex items-center gap-2 px-4 py-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition-colors font-medium"
                            >
                                <RefreshCw size={18} /> Reload
                            </button>
                            <button
                                onClick={this.handleGoHome}
                                className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors font-medium"
                            >
                                <Home size={18} /> Go Home
                            </button>
                        </div>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}
