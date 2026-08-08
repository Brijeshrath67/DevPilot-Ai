import {
  createContext,
  useCallback,
  useContext,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { createPortal } from "react-dom";
import { AlertCircle, AlertTriangle, CheckCircle2, Info, X } from "lucide-react";
import { cn } from "../../lib/utils";

type ToastVariant = "success" | "error" | "warning" | "info";

interface ToastItem {
  id: number;
  variant: ToastVariant;
  message: string;
}

interface ToastContextValue {
  toast: (variant: ToastVariant, message: string) => void;
  success: (message: string) => void;
  error: (message: string) => void;
  warning: (message: string) => void;
  info: (message: string) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

const icons: Record<ToastVariant, ReactNode> = {
  success: <CheckCircle2 className="h-4 w-4 text-success" />,
  error: <AlertCircle className="h-4 w-4 text-critical" />,
  warning: <AlertTriangle className="h-4 w-4 text-warning" />,
  info: <Info className="h-4 w-4 text-info" />,
};

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([]);
  const idRef = useRef(0);

  const dismiss = useCallback((id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const toast = useCallback(
    (variant: ToastVariant, message: string) => {
      const id = ++idRef.current;
      setToasts((prev) => [...prev.slice(-4), { id, variant, message }]);
      window.setTimeout(() => dismiss(id), 4500);
    },
    [dismiss]
  );

  const value: ToastContextValue = {
    toast,
    success: useCallback((m) => toast("success", m), [toast]),
    error: useCallback((m) => toast("error", m), [toast]),
    warning: useCallback((m) => toast("warning", m), [toast]),
    info: useCallback((m) => toast("info", m), [toast]),
  };

  return (
    <ToastContext.Provider value={value}>
      {children}
      {createPortal(
        <div
          aria-live="polite"
          className="pointer-events-none fixed right-4 top-4 z-[60] flex w-80 flex-col gap-2"
        >
          {toasts.map((item) => (
            <div
              key={item.id}
              role="status"
              className={cn(
                "pointer-events-auto flex animate-toast-in items-start gap-2.5 rounded-lg border border-line-2 bg-panel-4 px-3.5 py-3 shadow-overlay",
                item.variant === "success" && "border-success/25",
                item.variant === "error" && "border-critical/25",
                item.variant === "warning" && "border-warning/25",
                item.variant === "info" && "border-info/25"
              )}
            >
              <span className="mt-px">{icons[item.variant]}</span>
              <p className="flex-1 text-xs font-medium leading-relaxed text-ink-2">{item.message}</p>
              <button
                aria-label="Dismiss notification"
                onClick={() => dismiss(item.id)}
                className="text-ink-3 transition-colors hover:text-ink"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            </div>
          ))}
        </div>,
        document.body
      )}
    </ToastContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useToast(): ToastContextValue {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within ToastProvider");
  return ctx;
}
