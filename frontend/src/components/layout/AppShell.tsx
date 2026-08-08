import { useEffect, useState } from "react";
import { Outlet, useLocation } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";
import { CommandPalette } from "./CommandPalette";
import { cn } from "../../lib/utils";

export function AppShell() {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [commandOpen, setCommandOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    setDrawerOpen(false);
    setCommandOpen(false);
  }, [location.pathname]);

  return (
    <div className="min-h-screen bg-base text-ink-2">
      <div className="fixed inset-0 z-0 overflow-hidden" aria-hidden>
        <div className="absolute -left-32 -top-40 h-96 w-96 rounded-full bg-accent/[0.06] blur-3xl" />
        <div className="absolute right-0 top-1/3 h-80 w-80 rounded-full bg-accent-2/[0.05] blur-3xl" />
      </div>

      <div className="relative z-10 flex h-screen">
        <div className="hidden w-60 shrink-0 lg:block">
          <Sidebar />
        </div>

        {drawerOpen && (
          <div className="fixed inset-0 z-40 lg:hidden">
            <div
              className="absolute inset-0 bg-black/60 backdrop-blur-sm"
              onClick={() => setDrawerOpen(false)}
              aria-hidden
            />
            <div className="absolute inset-y-0 left-0 animate-drawer-in">
              <Sidebar onNavigate={() => setDrawerOpen(false)} />
            </div>
          </div>
        )}

        <div className="flex min-w-0 flex-1 flex-col">
          <Topbar onMenuClick={() => setDrawerOpen(true)} onOpenCommand={() => setCommandOpen(true)} />
          <main className={cn("scrollbar-thin flex-1 overflow-y-auto")}>
            <div className="mx-auto w-full max-w-[1180px] px-4 py-6 sm:px-6 lg:px-8">
              <Outlet />
            </div>
          </main>
        </div>
      </div>

      <CommandPalette open={commandOpen} onClose={() => setCommandOpen(false)} />
    </div>
  );
}
