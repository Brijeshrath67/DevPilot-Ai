import { useState } from "react";
import { useParams } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import api from "../lib/api";
import Sidebar from "../components/common/Sidebar";
import Header from "../components/common/Header";

interface Issue {
  severity: string;
  file: string;
  line: number;
  vulnerability: string;
  description: string;
  recommendation: string;
}

const SEVERITY_STYLES: Record<string, string> = {
  CRITICAL: "bg-rose-500/10 text-rose-400 border-rose-500/30",
  HIGH: "bg-orange-500/10 text-orange-400 border-orange-500/30",
  MEDIUM: "bg-amber-500/10 text-amber-400 border-amber-500/30",
  MINOR: "bg-sky-500/10 text-sky-400 border-sky-500/30",
};

export default function Review() {
  const { repoId } = useParams();
  const [reviewScope, setReviewScope] = useState("full");
  const [result, setResult] = useState<any>(null);

  const reviewMutation = useMutation(
    async () => {
      const res = await api.post(`/repos/${repoId}/code-review`, { review_scope: reviewScope });
      return res.data;
    },
    {
      onSuccess: (data) => setResult(data.data),
    }
  );

  // Parse issues from the LLM JSON response
  let issues: Issue[] = [];
  let recommendations: string[] = [];
  if (result?.issues) {
    try {
      const parsed = typeof result.issues === "string" ? JSON.parse(result.issues) : result;
      issues = parsed.issues || result.issues || [];
      recommendations = parsed.recommendations || result.recommendations || [];
    } catch {
      issues = Array.isArray(result.issues) ? result.issues : [];
      recommendations = result.recommendations || [];
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header />
        <main className="flex-1 p-8 space-y-6 max-w-5xl w-full mx-auto">

          {/* Page Header */}
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-7 shadow-xl">
            <h1 className="text-2xl font-extrabold text-white flex items-center gap-3">
              🛠️ Code Review
            </h1>
            <p className="text-sm text-slate-400 mt-2">
              Run an automated code audit and get severity-graded findings with concrete remediation steps.
            </p>

            {/* Scope Selector */}
            <div className="flex flex-wrap gap-2 mt-5">
              {["full", "security", "performance", "maintainability"].map((scope) => (
                <button
                  key={scope}
                  onClick={() => setReviewScope(scope)}
                  className={`px-4 py-1.5 rounded-lg text-xs font-semibold capitalize border transition-all ${
                    reviewScope === scope
                      ? "bg-sky-500/10 border-sky-500/40 text-sky-400"
                      : "border-slate-700 text-slate-400 hover:text-slate-200 hover:border-slate-600"
                  }`}
                >
                  {scope}
                </button>
              ))}
            </div>

            <button
              onClick={() => reviewMutation.mutate()}
              disabled={reviewMutation.isLoading}
              className="mt-5 bg-gradient-to-r from-orange-500 to-rose-600 hover:from-orange-400 hover:to-rose-500 text-white font-semibold py-2.5 px-6 rounded-xl text-sm transition-all shadow-lg shadow-orange-500/10 flex items-center gap-2 disabled:opacity-60"
            >
              {reviewMutation.isLoading ? (
                <><span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span> Analyzing Code...</>
              ) : "Run Code Review"}
            </button>
          </div>

          {/* Results */}
          {result && (
            <div className="space-y-4">
              {/* Summary Bar */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                {(["CRITICAL", "HIGH", "MEDIUM", "MINOR"] as const).map((sev) => {
                  const count = issues.filter((i: Issue) => i.severity === sev).length;
                  return (
                    <div key={sev} className={`p-4 rounded-2xl border text-center ${SEVERITY_STYLES[sev]}`}>
                      <div className="text-2xl font-extrabold">{count}</div>
                      <div className="text-[10px] font-bold uppercase tracking-widest mt-1">{sev}</div>
                    </div>
                  );
                })}
              </div>

              {/* Issues List */}
              {issues.length > 0 && (
                <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
                  <h2 className="text-base font-bold text-white">Findings</h2>
                  {issues.map((issue: Issue, idx: number) => (
                    <div key={idx} className="border border-slate-800 rounded-2xl p-5 bg-slate-950/60 space-y-3 hover:border-slate-700 transition-colors">
                      <div className="flex items-start justify-between gap-3 flex-wrap">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider border ${SEVERITY_STYLES[issue.severity] || SEVERITY_STYLES.MINOR}`}>
                            {issue.severity}
                          </span>
                          <span className="text-sm font-semibold text-white">{issue.vulnerability}</span>
                        </div>
                        <span className="font-mono text-[10px] text-slate-500 bg-slate-900 px-2 py-1 rounded-lg shrink-0">
                          {issue.file}:{issue.line}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 leading-relaxed">{issue.description}</p>
                      <div className="bg-emerald-500/5 border border-emerald-500/20 rounded-xl px-4 py-2.5">
                        <span className="text-[10px] font-bold uppercase text-emerald-500 block mb-1">Fix Recommendation</span>
                        <p className="text-xs text-emerald-300">{issue.recommendation}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Recommendations */}
              {recommendations.length > 0 && (
                <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl">
                  <h2 className="text-base font-bold text-white mb-4">General Recommendations</h2>
                  <ul className="space-y-2">
                    {recommendations.map((rec: string, i: number) => (
                      <li key={i} className="flex items-start gap-3 text-sm text-slate-300">
                        <span className="text-sky-400 mt-0.5">›</span>
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
