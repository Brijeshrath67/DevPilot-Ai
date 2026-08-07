import { useParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "../lib/api";
import Sidebar from "../components/common/Sidebar";
import Header from "../components/common/Header";

const METRICS = [
  { key: "documentation_score", label: "Documentation", icon: "📄", color: "from-sky-500 to-blue-600", trackColor: "#0ea5e9" },
  { key: "testing_score", label: "Testing", icon: "🧪", color: "from-emerald-500 to-teal-600", trackColor: "#10b981" },
  { key: "security_score", label: "Security", icon: "🛡️", color: "from-rose-500 to-red-600", trackColor: "#f43f5e" },
  { key: "maintainability_score", label: "Maintainability", icon: "⚙️", color: "from-violet-500 to-purple-600", trackColor: "#8b5cf6" },
  { key: "complexity_score", label: "Complexity", icon: "🔀", color: "from-amber-500 to-orange-600", trackColor: "#f59e0b" },
];

function ScoreDial({ value, color: _color, trackColor }: { value: number; color: string; trackColor: string }) {
  const r = 40;
  const circumference = 2 * Math.PI * r;
  const dashOffset = circumference - (value / 100) * circumference;

  return (
    <div className="relative w-24 h-24 mx-auto">
      <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
        <circle cx="50" cy="50" r={r} fill="none" stroke="#1e293b" strokeWidth="10" />
        <circle
          cx="50" cy="50" r={r}
          fill="none" stroke={trackColor} strokeWidth="10"
          strokeDasharray={circumference}
          strokeDashoffset={dashOffset}
          strokeLinecap="round"
          className="transition-all duration-700"
          style={{ filter: `drop-shadow(0 0 6px ${trackColor}60)` }}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-xl font-extrabold text-white">{Math.round(value)}</span>
      </div>
    </div>
  );
}

export default function Health() {
  const { repoId } = useParams();
  const queryClient = useQueryClient();

  const { data: healthData, isLoading } = useQuery(
    ["health", repoId],
    async () => {
      const res = await api.get(`/repos/${repoId}/health`);
      return res.data;
    },
    { enabled: Boolean(repoId) }
  );

  const securityMutation = useMutation(
    async () => {
      const res = await api.post(`/repos/${repoId}/security`);
      return res.data;
    },
    {
      onSuccess: () => queryClient.invalidateQueries(["health", repoId]),
    }
  );

  const health = healthData?.data;

  const getGrade = (score: number) => {
    if (score >= 90) return { grade: "A+", color: "text-emerald-400" };
    if (score >= 80) return { grade: "A", color: "text-emerald-400" };
    if (score >= 70) return { grade: "B", color: "text-sky-400" };
    if (score >= 60) return { grade: "C", color: "text-amber-400" };
    return { grade: "D", color: "text-rose-400" };
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header />
        <main className="flex-1 p-8 space-y-6 max-w-5xl w-full mx-auto">

          {/* Header */}
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-7 shadow-xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl font-extrabold text-white flex items-center gap-3">❤️ Project Health</h1>
              <p className="text-sm text-slate-400 mt-1">Live scorecards across key quality dimensions.</p>
            </div>
            <div className="flex gap-3 flex-wrap">
              <button
                onClick={() => queryClient.invalidateQueries(["health", repoId])}
                className="text-xs font-semibold text-slate-400 hover:text-slate-200 border border-slate-700 px-4 py-2 rounded-xl transition-all"
              >
                Refresh
              </button>
              <button
                onClick={() => securityMutation.mutate()}
                disabled={securityMutation.isLoading}
                className="bg-gradient-to-r from-rose-500 to-pink-600 hover:from-rose-400 hover:to-pink-500 text-white font-semibold py-2 px-5 rounded-xl text-sm transition-all shadow-lg shadow-rose-500/10 flex items-center gap-2 disabled:opacity-60"
              >
                {securityMutation.isLoading ? (
                  <><span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span> Scanning...</>
                ) : "🔍 Run Security Scan"}
              </button>
            </div>
          </div>

          {isLoading ? (
            <div className="flex items-center justify-center py-32">
              <div className="w-10 h-10 border-4 border-pink-500/20 border-t-pink-500 rounded-full animate-spin"></div>
            </div>
          ) : health ? (
            <>
              {/* Overall Score Banner */}
              <div className="bg-gradient-to-r from-slate-900 via-indigo-950/30 to-slate-900 border border-slate-800 rounded-3xl p-8 flex flex-col sm:flex-row items-center gap-6 shadow-xl">
                <div className="w-32 h-32 mx-auto sm:mx-0 relative">
                  <ScoreDial value={health.overall_score ?? 0} color="from-sky-500 to-indigo-600" trackColor="#6366f1" />
                </div>
                <div className="text-center sm:text-left">
                  <p className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-1">Overall Health Score</p>
                  <div className="text-6xl font-extrabold text-white">{Math.round(health.overall_score ?? 0)}</div>
                  <div className={`text-xl font-bold mt-1 ${getGrade(health.overall_score ?? 0).color}`}>
                    Grade {getGrade(health.overall_score ?? 0).grade}
                  </div>
                </div>
              </div>

              {/* Score Cards Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
                {METRICS.map((m) => {
                  const score = health[m.key] ?? 0;
                  const { grade, color } = getGrade(score);
                  return (
                    <div key={m.key} className="bg-slate-900 border border-slate-800 rounded-2xl p-5 flex flex-col items-center gap-3 hover:border-slate-700 transition-all shadow-md">
                      <ScoreDial value={score} color={m.color} trackColor={m.trackColor} />
                      <div className="text-center space-y-0.5">
                        <div className="text-[10px] font-bold uppercase tracking-widest text-slate-400">{m.label}</div>
                        <div className={`text-sm font-bold ${color}`}>Grade {grade}</div>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Recommendations */}
              {health.recommendations && health.recommendations.length > 0 && (
                <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl">
                  <h2 className="text-base font-bold text-white mb-4 flex items-center gap-2">
                    📋 Action Items
                    <span className="text-xs text-slate-500 font-normal ml-1">{health.recommendations.length} items</span>
                  </h2>
                  <div className="space-y-3">
                    {health.recommendations.map((rec: string, i: number) => {
                      const isCritical = rec.startsWith("CRITICAL");
                      const isHigh = rec.startsWith("HIGH");
                      return (
                        <div key={i} className={`flex items-start gap-3 p-4 rounded-xl border text-sm ${
                          isCritical
                            ? "bg-rose-500/5 border-rose-500/20 text-rose-300"
                            : isHigh
                              ? "bg-orange-500/5 border-orange-500/20 text-orange-300"
                              : "bg-slate-800/50 border-slate-700/50 text-slate-300"
                        }`}>
                          <span>{isCritical ? "🚨" : isHigh ? "⚠️" : "ℹ️"}</span>
                          <span>{rec}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="py-20 text-center text-slate-500 text-sm border-2 border-dashed border-slate-800 rounded-3xl">
              Run analysis first to compute health metrics.
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
