import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate, Link } from "react-router-dom";
import api from "../lib/api";
import Sidebar from "../components/common/Sidebar";
import Header from "../components/common/Header";

interface Repository {
  repository_id: number;
  name: string;
  source_url: string | null;
  status: string;
  summary: string | null;
  created_at: string | null;
}

export default function Dashboard() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [sourceType, setSourceType] = useState<"github_url" | "archive">("github_url");
  const [sourceValue, setSourceValue] = useState("");
  const [repoName, setRepoName] = useState("");
  const [archiveFile, setArchiveFile] = useState<File | null>(null);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  // Fetch repositories
  const { data: reposData, isLoading, error } = useQuery({
    queryKey: ["repositories"],
    queryFn: async () => {
      const res = await api.get("/repos");
      return res.data;
    },
  });

  const repos: Repository[] = reposData?.data || [];

  // Mutation to upload repository
  const uploadMutation = useMutation(
    async (formData: FormData) => {
      const res = await api.post("/repos/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      return res.data;
    },
    {
      onSuccess: async (data) => {
        const newRepoId = data.data.repository_id;
        setMessage({ type: "success", text: `Repository "${data.data.name}" ingested successfully! Initiating analysis...` });

        // Clear inputs
        setSourceValue("");
        setRepoName("");
        setArchiveFile(null);

        // Refresh repository list
        queryClient.invalidateQueries({ queryKey: ["repositories"] });

        // Auto-trigger analyze
        try {
          await api.post(`/repos/${newRepoId}/analyze`, { analysis_scope: "full" });
          setMessage({ type: "success", text: `Repository ingested and analysis complete!` });
          setTimeout(() => navigate(`/repo/${newRepoId}`), 1500);
        } catch (err: any) {
          setMessage({ type: "success", text: `Repository ingested! Navigate to view details.` });
          setTimeout(() => navigate(`/repo/${newRepoId}`), 2000);
        }
      },
      onError: (err: any) => {
        setMessage({ type: "error", text: err.response?.data?.detail || "Failed to ingest repository." });
      },
    }
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);

    const formData = new FormData();
    formData.append("source_type", sourceType);

    if (sourceType === "github_url") {
      if (!sourceValue.trim()) {
        setMessage({ type: "error", text: "Please enter a GitHub repository URL." });
        return;
      }
      formData.append("source_value", sourceValue.trim());
      if (repoName.trim()) {
        formData.append("repository_name", repoName.trim());
      }
    } else {
      if (!archiveFile) {
        setMessage({ type: "error", text: "Please select a repository ZIP archive." });
        return;
      }
      formData.append("archive", archiveFile);
      if (repoName.trim()) {
        formData.append("repository_name", repoName.trim());
      }
    }

    uploadMutation.mutate(formData);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header />

        <main className="flex-1 p-8 space-y-8 max-w-6xl w-full mx-auto">
          {/* Welcome Header */}
          <div className="bg-gradient-to-r from-slate-900 via-indigo-950/20 to-slate-900 border border-slate-800 rounded-3xl p-8 shadow-xl relative overflow-hidden">
            <div className="absolute top-0 right-0 w-80 h-80 bg-sky-500/5 rounded-full blur-3xl -mr-16 -mt-16"></div>
            <div className="relative z-10 space-y-2">
              <h1 className="text-3xl font-extrabold text-white tracking-tight sm:text-4xl bg-gradient-to-r from-white via-slate-100 to-sky-400 bg-clip-text text-transparent">
                Developer Productivity, Unleashed.
              </h1>
              <p className="text-slate-400 max-w-2xl text-sm sm:text-base leading-relaxed">
                Connect your codebase to run instantaneous code audits, security scans, unit test scaffolding, and markdown documentation generation.
              </p>
            </div>
          </div>

          <div className="grid gap-8 md:grid-cols-3">
            {/* Ingestion Panel */}
            <section className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-6 md:col-span-1">
              <div>
                <h2 className="text-lg font-bold text-white">Ingest Repository</h2>
                <p className="text-xs text-slate-400 mt-1">Upload a zip archive or enter a public GitHub link.</p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Source Selection */}
                <div className="grid grid-cols-2 gap-2 bg-slate-950 p-1 rounded-xl border border-slate-800/80">
                  <button
                    type="button"
                    onClick={() => { setSourceType("github_url"); setMessage(null); }}
                    className={`py-2 px-3 rounded-lg text-xs font-semibold tracking-wide transition-all ${
                      sourceType === "github_url"
                        ? "bg-slate-800 text-sky-400 shadow-sm"
                        : "text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    GitHub URL
                  </button>
                  <button
                    type="button"
                    onClick={() => { setSourceType("archive"); setMessage(null); }}
                    className={`py-2 px-3 rounded-lg text-xs font-semibold tracking-wide transition-all ${
                      sourceType === "archive"
                        ? "bg-slate-800 text-sky-400 shadow-sm"
                        : "text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    ZIP File
                  </button>
                </div>

                {/* Input Fields */}
                <div className="space-y-3">
                  <div className="space-y-1">
                    <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Project Name (Optional)</label>
                    <input
                      type="text"
                      placeholder="e.g. My Awesome WebApp"
                      value={repoName}
                      onChange={(e) => setRepoName(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-sky-500 transition-colors"
                    />
                  </div>

                  {sourceType === "github_url" ? (
                    <div className="space-y-1">
                      <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">GitHub URL</label>
                      <input
                        type="url"
                        placeholder="https://github.com/user/repo"
                        value={sourceValue}
                        onChange={(e) => setSourceValue(e.target.value)}
                        className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-sky-500 transition-colors"
                      />
                    </div>
                  ) : (
                    <div className="space-y-1">
                      <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">ZIP File Upload</label>
                      <input
                        type="file"
                        accept=".zip"
                        onChange={(e) => setArchiveFile(e.target.files?.[0] || null)}
                        className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-400 focus:outline-none focus:border-sky-500 file:mr-2 file:py-1 file:px-2 file:rounded-lg file:border-0 file:text-[10px] file:font-semibold file:bg-sky-500/10 file:text-sky-400 hover:file:bg-sky-500/20"
                      />
                    </div>
                  )}
                </div>

                {message && (
                  <div className={`p-3 rounded-xl text-xs font-medium border ${
                    message.type === "success"
                      ? "bg-emerald-500/5 border-emerald-500/20 text-emerald-400"
                      : "bg-rose-500/5 border-rose-500/20 text-rose-400"
                  }`}>
                    {message.text}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={uploadMutation.isLoading}
                  className="w-full bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white font-semibold py-2.5 rounded-xl text-sm transition-all duration-200 shadow-lg shadow-sky-500/10 hover:shadow-sky-500/25 flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {uploadMutation.isLoading ? (
                    <>
                      <span className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin"></span>
                      Ingesting...
                    </>
                  ) : (
                    "Ingest & Analyze"
                  )}
                </button>
              </form>
            </section>

            {/* Repositories List */}
            <section className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl md:col-span-2 space-y-6">
              <div>
                <h2 className="text-lg font-bold text-white">Ingested Repositories</h2>
                <p className="text-xs text-slate-400 mt-1">Select an active workspace workspace to begin analysis.</p>
              </div>

              {isLoading ? (
                <div className="py-12 text-center text-slate-500 text-sm">Loading workspaces...</div>
              ) : error ? (
                <div className="py-12 text-center text-rose-400 text-sm">Failed to retrieve repositories.</div>
              ) : repos.length === 0 ? (
                <div className="py-12 text-center border-2 border-dashed border-slate-800 rounded-2xl">
                  <span className="text-3xl">📭</span>
                  <p className="text-slate-500 text-xs mt-2">No repositories ingested yet.</p>
                </div>
              ) : (
                <div className="grid gap-4 sm:grid-cols-2">
                  {repos.map((repo) => (
                    <Link
                      key={repo.repository_id}
                      to={`/repo/${repo.repository_id}`}
                      className="group p-5 bg-slate-950 border border-slate-800/80 rounded-2xl hover:border-slate-700/80 transition-all duration-200 flex flex-col justify-between space-y-3 relative overflow-hidden"
                    >
                      <div className="absolute top-0 right-0 w-24 h-24 bg-sky-500/5 rounded-full blur-2xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
                      <div className="space-y-1 relative z-10">
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-slate-500 font-semibold uppercase tracking-wider">Workspace #{repo.repository_id}</span>
                          <span className={`px-2 py-0.5 rounded-full text-[9px] font-semibold capitalize ${
                            repo.status === "analyzed"
                              ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                              : "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                          }`}>
                            {repo.status}
                          </span>
                        </div>
                        <h3 className="font-bold text-white group-hover:text-sky-400 transition-colors text-base truncate pr-4">{repo.name}</h3>
                        <p className="text-xs text-slate-400 line-clamp-2 h-8 leading-relaxed mt-1">
                          {repo.summary || (repo.source_url ? `Imported from: ${repo.source_url}` : "Workspace folder successfully ingested.")}
                        </p>
                      </div>

                      <div className="flex items-center justify-between border-t border-slate-800/60 pt-3 text-[11px] text-slate-500 font-medium">
                        <span>{repo.created_at ? new Date(repo.created_at).toLocaleDateString() : "Just now"}</span>
                        <span className="text-sky-400 group-hover:translate-x-1 transition-transform">Configure workspace &rarr;</span>
                      </div>
                    </Link>
                  ))}
                </div>
              )}
            </section>
          </div>
        </main>
      </div>
    </div>
  );
}
