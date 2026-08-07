import { useParams, Link } from "react-router-dom";
import { useQuery, useMutation } from "@tanstack/react-query";
import api from "../lib/api";
import Sidebar from "../components/common/Sidebar";
import Header from "../components/common/Header";

export default function Repository() {
  const { repoId } = useParams();

  const { data: repoData, isLoading } = useQuery(["repo", repoId], async () => {
    const res = await api.get(`/repos/${repoId}`);
    return res.data;
  }, { enabled: Boolean(repoId) });

  const { data: filesData } = useQuery(["repoFiles", repoId], async () => {
    const res = await api.get(`/repos/${repoId}/files`);
    return res.data;
  }, { enabled: Boolean(repoId) });

  const analyzeMutation = useMutation(async () => {
    const res = await api.post(`/repos/${repoId}/analyze`, { analysis_scope: "full" });
    return res.data;
  });

  const repo = repoData?.data;
  const files: any[] = filesData?.data || [];

  const filesByLanguage: Record<string, string[]> = {};
  files.forEach((f) => {
    const lang = f.language || "Other";
    if (!filesByLanguage[lang]) filesByLanguage[lang] = [];
    filesByLanguage[lang].push(f.file_path);
  });

  const quickLinks = [
    { label: "Code Review", path: `/repo/${repoId}/review`, icon: "🛠️", color: "from-orange-500/10 to-rose-500/10 border-orange-500/20 text-orange-400" },
    { label: "Documentation", path: `/repo/${repoId}/docs`, icon: "📝", color: "from-sky-500/10 to-blue-500/10 border-sky-500/20 text-sky-400" },
    { label: "Unit Tests", path: `/repo/${repoId}/tests`, icon: "🧪", color: "from-emerald-500/10 to-teal-500/10 border-emerald-500/20 text-emerald-400" },
    { label: "QA Chat", path: `/repo/${repoId}/chat`, icon: "💬", color: "from-violet-500/10 to-purple-500/10 border-violet-500/20 text-violet-400" },
    { label: "Health Score", path: `/repo/${repoId}/health`, icon: "❤️", color: "from-pink-500/10 to-rose-500/10 border-pink-500/20 text-pink-400" },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header />
        <main className="flex-1 p-8 space-y-6 max-w-6xl w-full mx-auto">
          {isLoading ? (
            <div className="flex items-center justify-center py-32">
              <div className="w-10 h-10 border-4 border-sky-500/20 border-t-sky-500 rounded-full animate-spin"></div>
            </div>
          ) : (
            <>
              {/* Repository Header Card */}
              <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-xl relative overflow-hidden">
                <div className="absolute -top-16 -right-16 w-48 h-48 bg-sky-500/5 rounded-full blur-3xl"></div>
                <div className="relative z-10 flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
                  <div className="space-y-2">
                    <div className="flex items-center gap-3">
                      <span className="text-3xl">📁</span>
                      <h1 className="text-2xl font-extrabold text-white">{repo?.name || "Repository Workspace"}</h1>
                    </div>
                    <p className="text-sm text-slate-400 max-w-2xl leading-relaxed">
                      {repo?.summary || "Run analysis to generate a project summary."}
                    </p>
                    <div className="flex items-center gap-3 flex-wrap pt-1">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold border capitalize ${
                        repo?.status === "analyzed"
                          ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                          : "bg-amber-500/10 text-amber-400 border-amber-500/20"
                      }`}>
                        {repo?.status || "pending"}
                      </span>
                      {repo?.source_url && (
                        <a href={repo.source_url} target="_blank" rel="noreferrer" className="text-xs text-sky-400 hover:underline truncate max-w-xs">
                          {repo.source_url}
                        </a>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={() => analyzeMutation.mutate()}
                    disabled={analyzeMutation.isLoading}
                    className="shrink-0 bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white font-semibold py-2.5 px-5 rounded-xl text-sm transition-all shadow-lg shadow-sky-500/10 flex items-center gap-2 disabled:opacity-60"
                  >
                    {analyzeMutation.isLoading ? (
                      <><span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span> Analyzing...</>
                    ) : "Re-run Analysis"}
                  </button>
                </div>
              </div>

              {/* Architecture Summary */}
              {repo?.architecture_summary && (
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-lg">
                  <h2 className="text-sm font-bold uppercase tracking-widest text-slate-400 mb-3">Architecture Summary</h2>
                  <p className="text-slate-300 text-sm leading-relaxed">{repo.architecture_summary}</p>
                </div>
              )}

              {/* Quick Action Cards */}
              <div>
                <h2 className="text-sm font-bold uppercase tracking-widest text-slate-500 mb-4">Quick Actions</h2>
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
                  {quickLinks.map((ql) => (
                    <Link
                      key={ql.label}
                      to={ql.path}
                      className={`group bg-gradient-to-br ${ql.color} border rounded-2xl p-5 flex flex-col items-center justify-center gap-2 text-center hover:scale-105 transition-all duration-200 shadow-sm`}
                    >
                      <span className="text-2xl">{ql.icon}</span>
                      <span className="text-xs font-semibold">{ql.label}</span>
                    </Link>
                  ))}
                </div>
              </div>

              {/* File Tree */}
              <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl">
                <h2 className="text-base font-bold text-white mb-4 flex items-center gap-2">
                  🗂️ File Index
                  <span className="text-xs text-slate-500 font-normal">({files.length} files)</span>
                </h2>
                {files.length === 0 ? (
                  <div className="py-8 text-center text-slate-500 text-sm border-2 border-dashed border-slate-800 rounded-xl">
                    Run analysis to index files.
                  </div>
                ) : (
                  <div className="space-y-4">
                    {Object.entries(filesByLanguage).map(([lang, paths]) => (
                      <div key={lang}>
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-xs font-bold uppercase tracking-widest text-slate-400">{lang}</span>
                          <span className="text-xs text-slate-600">({paths.length})</span>
                        </div>
                        <div className="grid gap-1">
                          {paths.slice(0, 8).map((p) => (
                            <div key={p} className="font-mono text-xs text-slate-400 bg-slate-950/60 border border-slate-800/60 rounded-lg px-3 py-1.5 truncate hover:text-slate-200 transition-colors">
                              {p}
                            </div>
                          ))}
                          {paths.length > 8 && (
                            <div className="text-xs text-slate-500 px-3 py-1">
                              + {paths.length - 8} more files...
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </>
          )}
        </main>
      </div>
    </div>
  );
}
