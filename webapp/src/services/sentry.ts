import * as Sentry from "@sentry/react";
import { BrowserTracing } from "@sentry/tracing";

export const initSentry = () => {
    const dsn = import.meta.env.VITE_SENTRY_DSN;
    const environment = import.meta.env.VITE_ENVIRONMENT || 'development';

    if (!dsn) {
        console.warn('⚠️  Sentry DSN not configured - error monitoring disabled');
        return;
    }

    Sentry.init({
        dsn,
        environment,

        // Performance monitoring
        integrations: [new BrowserTracing()],
        tracesSampleRate: environment === 'production' ? 0.1 : 1.0,

        // Session tracking
        replaysSessionSampleRate: 0.1,
        replaysOnErrorSampleRate: 1.0,

        // Custom filters
        beforeSend(event, hint) {
            // Remove sensitive data
            if (event.request) {
                // Remove authorization headers
                if (event.request.headers) {
                    delete event.request.headers['Authorization'];
                    delete event.request.headers['Cookie'];
                }

                // Remove sensitive query params
                if (event.request.query_string) {
                    const sensitiveParams = ['password', 'token', 'api_key'];
                    sensitiveParams.forEach(param => {
                        const qs = event.request?.query_string;
                        if (typeof qs === 'string' && qs.includes(param)) {
                            event.request!.query_string = '[REDACTED]';
                        }
                    });
                }
            }

            return event;
        },
    });

    console.log(`✅ Sentry initialized (environment: ${environment})`);
};

// Error boundary component
export const ErrorBoundary = Sentry.ErrorBoundary;

// Manual error capture
export const captureException = Sentry.captureException;
export const captureMessage = Sentry.captureMessage;

// User context
export const setUser = (userId: string, email?: string, schoolId?: string) => {
    Sentry.setUser({
        id: userId,
        email,
        school_id: schoolId
    });
};
