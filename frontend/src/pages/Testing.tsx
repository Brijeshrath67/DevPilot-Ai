import { useState } from "react";
import { useParams } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import api from "../lib/api";
import Sidebar from "../components/common/Sidebar";
import Header from "../components/common/Header";

const TEST_TYPES = [
  { id: "unit", label: "Unit Tests", icon: "🧪", description: "Isolated function and class-level assertions." },
  { id: "integration", label: "Integration Tests", icon: "🔗", description: "API endpoint and cross-module flow tests." },
  { id: "edge_cases", label: "Edge Cases", icon: "🎯", description: "Boundary conditions and null-value scenarios." },
];

export default function Testing() {
  const { repoId } = useParams();
  const [selected, setSelected] = useState<string[]>(["unit"]);
  const [generated, setGenerated] = useState<{ type: string; content: string }[]>([]);
  const [activeTab, setActiveTab] = useState<string | null>(null);
  const [copied, setCopied] = useState<string | null>(null);

  const generateMutation = useMutation(
    async () => {
      const res = await api.post(`/repos/${repoId}/tests`, { test_types: selected });
      return res.data;
    },
    {
      onSuccess: (data) => {
        const tests = data.data?.tests || [];
        setGenerated(tests);
        if (tests.length > 0) setActiveTab(tests[0].type);
      },
    }
  );

  const toggle = (id: string) => setSelected((p) => p.includes(id) ? p.filter((x) => x !== id) : [...p, id]);

  const copy = (type: string, content: string) => {
    navigator.clipboard.writeText(content).then(() => {
      setCopied(type);
      setTimeout(() => setCopied(null), 2000);
    });
  };

  const activeTest = generated.find((t) => t.type === activeTab);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header />
        <main className="flex-1 p-8 space-y-6 max-w-5xl w-full mx-auto">

          {/* Header Panel */}
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-7 shadow-xl">
            <h1 className="text-2xl font-extrabold text-white flex items-center gap-3">🧪 Test Generator</h1>
            <p className="text-sm text-slate-400 mt-2">
              Automatically scaffold pytest test suites based on your repository's source code.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-5">
              {TEST_TYPES.map((tt) => (
                <button
                  key={tt.id}
                  onClick={() => toggle(tt.id)}
                  className={`flex flex-col items-start gap-2 p-5 rounded-2xl border text-left transition-all duration-200 ${
                    selected.includes(tt.id)
                      ? "bg-emerald-500/10 border-emerald-500/40 text-emerald-300"
                      : "border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200"
                  }`}
                >
                  <span className="text-2xl">{tt.icon}</span>
                  <div>
                    <div className="text-sm font-bold">{tt.label}</div>
                    <div className="text-xs text-slate-500 mt-0.5 leading-relaxed">{tt.description}</div>
                  </div>
                </button>
              ))}
            </div>

            <div className="mt-5 flex items-center justify-between flex-wrap gap-3">
              <span className="text-xs text-slate-500">{selected.length} test suite{selected.length !== 1 ? "s" : ""} selected</span>
              <button
                onClick={() => generateMutation.mutate()}
                disabled={selected.length === 0 || generateMutation.isLoading}
                className="bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-white font-semibold py-2.5 px-6 rounded-xl text-sm transition-all shadow-lg shadow-emerald-500/10 flex items-center gap-2 disabled:opacity-60"
              >
                {generateMutation.isLoading ? (
                  <><span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span> Generating...</>
                ) : "Generate Tests"}
              </button>
            </div>
          </div>

          {/* Output */}
          {generated.length > 0 && (
            <div className="bg-slate-900 border border-slate-800 rounded-3xl shadow-xl overflow-hidden">
              {/* Tabs */}
              <div className="flex border-b border-slate-800">
                {generated.map((t) => {
                  const meta = TEST_TYPES.find((x) => x.id === t.type);
                  return (
                    <button
                      key={t.type}
                      onClick={() => setActiveTab(t.type)}
                      className={`flex items-center gap-2 px-5 py-3 text-xs font-semibold whitespace-nowrap border-b-2 transition-all ${
                        activeTab === t.type
                          ? "border-emerald-500 text-emerald-400"
                          : "border-transparent text-slate-400 hover:text-slate-200"
                      }`}
                    >
                      {meta?.icon} {meta?.label || t.type}
                    </button>
                  );
                })}
              </div>

              {/* Code Block */}
              {activeTest && (
                <div className="relative">
                  <div className="flex items-center justify-between px-6 py-3 bg-slate-950/60 border-b border-slate-800/60">
                    <span className="text-xs font-mono text-slate-500">test_{activeTest.type}.py</span>
                    <button
                      onClick={() => copy(activeTest.type, activeTest.content)}
                      className="text-xs font-semibold text-slate-400 hover:text-slate-200 bg-slate-800 border border-slate-700 px-3 py-1 rounded-lg transition-all flex items-center gap-1.5"
                    >
                      {copied === activeTest.type ? "✅ Copied!" : "📋 Copy"}
                    </button>
                  </div>
                  <pre className="text-sm text-emerald-300 font-mono whitespace-pre-wrap leading-relaxed p-6 overflow-x-auto max-h-[500px] overflow-y-auto">
                    {activeTest.content || "# No test content generated."}
                  </pre>
                </div>
              )}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
