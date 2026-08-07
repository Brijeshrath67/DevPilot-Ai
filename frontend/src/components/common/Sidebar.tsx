import { NavLink, useParams } from "react-router-dom";

export default function Sidebar() {
  const { repoId } = useParams();

  const links = [
    { name: "Dashboard", path: "/", icon: "📁", alwaysEnabled: true },
    { name: "Overview", path: `/repo/${repoId}`, icon: "🔍", alwaysEnabled: false },
    { name: "Code Review", path: `/repo/${repoId}/review`, icon: "🛠️", alwaysEnabled: false },
    { name: "Documentation", path: `/repo/${repoId}/docs`, icon: "📝", alwaysEnabled: false },
    { name: "Unit Testing", path: `/repo/${repoId}/tests`, icon: "🧪", alwaysEnabled: false },
    { name: "QA Chat", path: `/repo/${repoId}/chat`, icon: "💬", alwaysEnabled: false },
    { name: "Health Score", path: `/repo/${repoId}/health`, icon: "❤️", alwaysEnabled: false },
    { name: "Settings", path: `/repo/${repoId}/settings`, icon: "⚙️", alwaysEnabled: false },
  ];

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col min-h-screen text-slate-200">
      <div className="p-6 border-b border-slate-800 flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center font-bold text-white text-lg shadow-lg shadow-sky-500/20">
          D
        </div>
        <div>
          <span className="font-semibold text-lg text-white block leading-none">DevPilot AI</span>
          <span className="text-[10px] text-sky-400 font-medium uppercase tracking-widest mt-1 block">Productivity Suite</span>
        </div>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {links.map((link) => {
          const enabled = link.alwaysEnabled || Boolean(repoId);
          if (!enabled) return null;

          return (
            <NavLink
              key={link.name}
              to={link.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? "bg-gradient-to-r from-sky-500/10 to-indigo-500/10 text-sky-400 border-l-2 border-sky-500 shadow-inner"
                    : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-200"
                }`
              }
            >
              <span className="text-base">{link.icon}</span>
              <span>{link.name}</span>
            </NavLink>
          );
        })}
      </nav>

      <div className="p-4 border-t border-slate-800 text-xs text-slate-500 text-center">
        v0.1.0 &copy; 2026
      </div>
    </aside>
  );
}
