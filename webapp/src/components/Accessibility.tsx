/**
 * Accessibility(WCAG 2.1) Components
 * Makes the app usable for people with disabilities
 */

import { useEffect, useRef } from 'react';

// Skip to main content link
export const SkipToMain = () => {
    return (
        <a
            href="#main-content"
            className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-blue-600 focus:text-white focus:rounded-lg"
            aria-label="Skip to main content"
        >
            Skip to main content
        </a>
    );
};

// Accessible button with proper ARIA
export const AccessibleButton = ({
    children,
    onClick,
    disabled = false,
    ariaLabel,
    ariaDescribedBy,
    variant = 'primary'
}: {
    children: React.ReactNode;
    onClick: () => void;
    disabled?: boolean;
    ariaLabel?: string;
    ariaDescribedBy?: string;
    variant?: 'primary' | 'secondary' | 'danger';
}) => {
    return (
        <button
            onClick={onClick}
            disabled={disabled}
            aria-label={ariaLabel}
            aria-describedby={ariaDescribedBy}
            aria-disabled={disabled}
            className={`
        px-4 py-2 rounded-lg font-medium transition-colors
        focus:outline-none focus:ring-2 focus:ring-offset-2
        ${variant === 'primary' ? 'bg-blue-600 hover:bg-blue-500 focus:ring-blue-500' : ''}
        ${variant === 'secondary' ? 'bg-slate-600 hover:bg-slate-500 focus:ring-slate-500' : ''}
        ${variant === 'danger' ? 'bg-red-600 hover:bg-red-500 focus:ring-red-500' : ''}
        ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
      `}
        >
            {children}
        </button>
    );
};

// Form input with proper labels and ARIA
export const AccessibleInput = ({
    id,
    label,
    type = 'text',
    value,
    onChange,
    required = false,
    error,
    helperText,
    ...props
}: {
    id: string;
    label: string;
    type?: string;
    value: string;
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    required?: boolean;
    error?: string;
    helperText?: string;
    [key: string]: any;
}) => {
    const helperId = `${id}-helper`;
    const errorId = `${id}-error`;

    return (
        <div className="space-y-1">
            <label
                htmlFor={id}
                className="block text-sm font-medium text-slate-300"
            >
                {label}
                {required && <span className="text-red-500 ml-1" aria-label="required">*</span>}
            </label>

            <input
                id={id}
                type={type}
                value={value}
                onChange={onChange}
                required={required}
                aria-required={required}
                aria-invalid={!!error}
                aria-describedby={`${helperText ? helperId : ''} ${error ? errorId : ''}`.trim()}
                className={`
          w-full px-3 py-2 bg-slate-700 border rounded-lg
          focus:outline-none focus:ring-2 focus:ring-blue-500
          ${error ? 'border-red-500' : 'border-slate-600'}
        `}
                {...props}
            />

            {helperText && (
                <p id={helperId} className="text-sm text-slate-400">
                    {helperText}
                </p>
            )}

            {error && (
                <p id={errorId} className="text-sm text-red-500" role="alert">
                    {error}
                </p>
            )}
        </div>
    );
};

// Accessible modal/dialog
export const AccessibleModal = ({
    isOpen,
    onClose,
    title,
    children
}: {
    isOpen: boolean;
    onClose: () => void;
    title: string;
    children: React.ReactNode;
}) => {
    const modalRef = useRef<HTMLDivElement>(null);
    const previousFocus = useRef<HTMLElement | null>(null);

    useEffect(() => {
        if (isOpen) {
            // Store previous focus
            previousFocus.current = document.activeElement as HTMLElement;

            // Focus first focusable element in modal
            const focusableElements = modalRef.current?.querySelectorAll(
                'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );
            if (focusableElements && focusableElements.length > 0) {
                (focusableElements[0] as HTMLElement).focus();
            }

            // Trap focus in modal
            const handleTab = (e: KeyboardEvent) => {
                if (e.key === 'Tab') {
                    const focusableElements = modalRef.current?.querySelectorAll(
                        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
                    );
                    if (!focusableElements || focusableElements.length === 0) return;

                    const firstElement = focusableElements[0] as HTMLElement;
                    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

                    if (e.shiftKey && document.activeElement === firstElement) {
                        e.preventDefault();
                        lastElement.focus();
                    } else if (!e.shiftKey && document.activeElement === lastElement) {
                        e.preventDefault();
                        firstElement.focus();
                    }
                }

                // Close on Escape
                if (e.key === 'Escape') {
                    onClose();
                }
            };

            document.addEventListener('keydown', handleTab);

            return () => {
                document.removeEventListener('keydown', handleTab);
                // Restore previous focus
                previousFocus.current?.focus();
            };
        }
    }, [isOpen, onClose]);

    if (!isOpen) return null;

    return (
        <div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/70"
            role="dialog"
            aria-modal="true"
            aria-labelledby="modal-title"
        >
            <div
                ref={modalRef}
                className="bg-slate-800 rounded-lg p-6 max-w-2xl w-full mx-4"
            >
                <h2 id="modal-title" className="text-2xl font-bold mb-4">
                    {title}
                </h2>

                {children}

                <button
                    onClick={onClose}
                    className="mt-4 px-4 py-2 bg-slate-600 hover:bg-slate-500 rounded-lg"
                    aria-label="Close dialog"
                >
                    Close
                </button>
            </div>
        </div>
    );
};

// Screen reader only text
export const ScreenReaderOnly = ({ children }: { children: React.ReactNode }) => {
    return (
        <span className="sr-only">
            {children}
        </span>
    );
};
