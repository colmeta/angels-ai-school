import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Component } from "react";
import { AlertTriangle, RefreshCw, Home } from "lucide-react";
export class ErrorBoundary extends Component {
    constructor() {
        super(...arguments);
        this.state = {
            hasError: false,
            error: null,
            errorInfo: null,
        };
        this.handleReload = () => {
            window.location.reload();
        };
        this.handleGoHome = () => {
            window.location.href = "/";
        };
    }
    static getDerivedStateFromError(error) {
        return { hasError: true, error, errorInfo: null };
    }
    componentDidCatch(error, errorInfo) {
        console.error("Uncaught error:", error, errorInfo);
        this.setState({ errorInfo });
    }
    render() {
        if (this.state.hasError) {
            return (_jsx("div", { className: "min-h-screen flex items-center justify-center bg-slate-50 p-4 font-sans text-slate-900", children: _jsxs("div", { className: "max-w-md w-full bg-white rounded-2xl shadow-xl border border-slate-200 p-8 text-center", children: [_jsx("div", { className: "w-16 h-16 bg-red-100 text-red-600 rounded-full flex items-center justify-center mx-auto mb-6", children: _jsx(AlertTriangle, { size: 32 }) }), _jsx("h1", { className: "text-2xl font-bold mb-2", children: "Something went wrong" }), _jsx("p", { className: "text-slate-500 mb-6", children: "The application encountered an unexpected error." }), _jsxs("div", { className: "text-left bg-slate-100 p-4 rounded-lg mb-6 overflow-auto max-h-48 text-xs font-mono text-slate-700 border border-slate-200", children: [_jsx("p", { className: "font-bold text-red-600 mb-1", children: this.state.error?.toString() }), _jsx("pre", { className: "whitespace-pre-wrap", children: this.state.errorInfo?.componentStack })] }), _jsxs("div", { className: "flex gap-3 justify-center", children: [_jsxs("button", { onClick: this.handleReload, className: "flex items-center gap-2 px-4 py-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition-colors font-medium", children: [_jsx(RefreshCw, { size: 18 }), " Reload"] }), _jsxs("button", { onClick: this.handleGoHome, className: "flex items-center gap-2 px-4 py-2 bg-white border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors font-medium", children: [_jsx(Home, { size: 18 }), " Go Home"] })] })] }) }));
        }
        return this.props.children;
    }
}
