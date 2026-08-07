import { useRepo } from "../../hooks/useRepo";
import { useParams, Link } from "react-router-dom";

export default function Header() {
  const { repoId } = useParams();
  const { data } = useRepo(repoId || "");
  const repo = data?.data;

  return (
    <header className="h-16 border-b border-slate-800 bg-slate-900/60 backdrop-blur-md px-8 flex items-center justify-between text-slate-100">
      <div className="flex items-center gap-4">
        {repo ? (
          <>
            <div className="flex items-center gap-2">
              <span className="text-xl">📁</span>
              <h2 className="font-semibold text-white text-base">{repo.name}</h2>
            </div>
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
            <span className="text-xs text-slate-400 capitalize">{repo.status}</span>
          </>
        ) : (
          <h2 className="font-semibold text-white text-base">Dashboard</h2>
        )}
      </div>

      <div className="flex items-center gap-4">
        {repoId && (
          <Link
            to="/"
            className="text-xs text-sky-400 hover:text-sky-300 font-medium border border-sky-400/20 px-3 py-1.5 rounded-lg bg-sky-400/5 hover:bg-sky-400/10 transition-all duration-200"
          >
            Switch Repository
          </Link>
        )}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center font-bold text-slate-300 text-xs">
            JD
          </div>
          <span className="text-xs text-slate-400 font-medium hidden sm:inline">Developer</span>
        </div>
      </div>
    </header>
  );
}
