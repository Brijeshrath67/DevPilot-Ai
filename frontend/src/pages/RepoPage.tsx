import { useParams } from "react-router-dom";
import { useRepo } from "../hooks/useRepo";
import { useHealth } from "../hooks/useHealth";

function ScoreCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900 p-6 shadow-xl shadow-slate-900/20">
      <h3 className="text-sm font-medium uppercase tracking-[0.2em] text-slate-400">{label}</h3>
      <p className="mt-4 text-4xl font-semibold text-white">{value}</p>
    </div>
  );
}

export default function RepoPage() {
  const { repoId } = useParams();
  const { data, isLoading, error } = useRepo(repoId || "");
  const { data: healthData, isLoading: isHealthLoading } = useHealth(repoId || "");

  if (!repoId) {
    return <div className="min-h-screen bg-slate-950 text-slate-100 p-10">Missing repository id.</div>;
  }

  if (isLoading) {
    return <div className="min-h-screen bg-slate-950 text-slate-100 p-10">Loading repository...</div>;
  }

  if (error) {
    return <div className="min-h-screen bg-slate-950 text-slate-100 p-10">Failed to load repository.</div>;
  }

  const repo = data?.data;
  const health = healthData?.data;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-10">
      <div className="max-w-6xl mx-auto space-y-6">
        <div className="rounded-3xl border border-slate-800 bg-slate-900 p-8 shadow-xl shadow-slate-900/20">
          <h1 className="text-3xl font-semibold">{repo?.name || "Repository Workspace"}</h1>
          <p className="mt-2 text-slate-400">ID: {repo?.repository_id}</p>
          <p className="mt-4 text-slate-300">Status: {repo?.status}</p>
        </div>

        <div className="grid gap-6 md:grid-cols-3">
          <ScoreCard label="Documentation" value={health?.documentation_score ?? 0} />
          <ScoreCard label="Testing" value={health?.testing_score ?? 0} />
          <ScoreCard label="Security" value={health?.security_score ?? 0} />
          <ScoreCard label="Maintainability" value={health?.maintainability_score ?? 0} />
          <ScoreCard label="Complexity" value={health?.complexity_score ?? 0} />
          <ScoreCard label="Overall" value={health?.overall_score ?? 0} />
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <section className="rounded-3xl border border-slate-800 bg-slate-900 p-8 shadow-xl shadow-slate-900/20">
            <h2 className="text-xl font-semibold">Project Summary</h2>
            <p className="mt-3 text-slate-300">{repo?.summary || "No summary available yet."}</p>
          </section>
          <section className="rounded-3xl border border-slate-800 bg-slate-900 p-8 shadow-xl shadow-slate-900/20">
            <h2 className="text-xl font-semibold">Architecture Summary</h2>
            <p className="mt-3 text-slate-300">{repo?.architecture_summary || "No architecture summary available yet."}</p>
          </section>
        </div>
      </div>
    </div>
  );
}
