import { cn } from "../../lib/utils";

export interface Tab {
  id: string;
  label: string;
  badge?: number;
  disabled?: boolean;
}

export interface TabsProps {
  tabs: Tab[];
  active: string;
  onChange: (id: string) => void;
  className?: string;
}

export function Tabs({ tabs, active, onChange, className }: TabsProps) {
  return (
    <div role="tablist" className={cn("scrollbar-thin flex items-center gap-1 overflow-x-auto", className)}>
      {tabs.map((tab) => {
        const isActive = tab.id === active;
        return (
          <button
            key={tab.id}
            role="tab"
            aria-selected={isActive}
            disabled={tab.disabled}
            onClick={() => onChange(tab.id)}
            className={cn(
              "relative inline-flex shrink-0 items-center gap-1.5 whitespace-nowrap rounded-lg px-3 py-1.5 text-xs font-medium transition-all duration-150",
              isActive
                ? "bg-accent/10 text-accent shadow-[inset_0_0_0_1px_rgba(99,102,241,0.25)]"
                : "text-ink-3 hover:bg-panel-3 hover:text-ink-2",
              tab.disabled && "cursor-not-allowed opacity-40"
            )}
          >
            {tab.label}
            {typeof tab.badge === "number" && tab.badge > 0 && (
              <span className="rounded bg-panel-4 px-1 text-[10px] font-semibold text-ink-2">{tab.badge}</span>
            )}
          </button>
        );
      })}
    </div>
  );
}
