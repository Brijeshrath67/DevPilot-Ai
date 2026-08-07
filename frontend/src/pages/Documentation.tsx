import { useState } from "react";
import { useParams } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import api from "../lib/api";
import Sidebar from "../components/common/Sidebar";
import Header from "../components/common/Header";

const DOC_TYPES = [
  { id: "readme", label: "README.md", icon: "📄", description: "Project overview, setup guide, and usage." },
  { id: "api_docs", label: "API Docs", icon: "🔌", description: "Endpoint references, request schemas, and examples." },
  { id: "architecture_docs", label: "Architecture", icon: "🏗️", description: "System design diagrams and module breakdown." },
  { id: "installation_guide", label: "Install Guide", icon: "⚙️", description: "Environment setup and configuration steps." },
  { id: "changelog", label: "Changelog", icon: "📋", description: "Versioned history of feature releases and fixes." },
];

export default function Documentation() {
  const { repoId } = useParams();
  const [selected, setSelected] = useState<string[]>(["readme"]);
  const [generated, setGenerated] = useState<{ type: string; content: string }[]>([]);
  const [activeTab, setActiveTab] = useState<string | null>(null);
  const [copied, setCopied] = useState<string | null>(null);

  const generateMutation = useMutation(
    async () => {
      const res = await api.post(`/repos/${repoId}/documentation`, { doc_types: selected });
      return res.data;
    },
    {
      onSuccess: (data) => {
        const docs = data.data?.documents || [];
        setGenerated(docs);
        if (docs.length > 0) setActiveTab(docs[0].type);
      },
    }
  );

  const toggleDoc = (id: string) => {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((d) => d !== id) : [...prev, id]
    );
  };

  const copyContent = (type: string, content: string) => {
    navigator.clipboard.writeText(content).then(() => {
      setCopied(type);
      setTimeout(() => setCopied(null), 2000);
    });
  };

  const activeDoc = generated.find((d) => d.type === activeTab);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header />
        <main className="flex-1 p-8 space-y-6 max-w-5xl w-full mx-auto">

          {/* Header */}
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-7 shadow-xl">
            <h1 className="text-2xl font-extrabold text-white flex items-center gap-3">📝 Documentation Generator</h1>
            <p className="text-sm text-slate-400 mt-2">
              Select the documentation types you want to generate for this repository.
            </p>

            {/* Doc type grid */}
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 mt-5">
              {DOC_TYPES.map((dt) => (
                <button
                  key={dt.id}
                  onClick={() => toggleDoc(dt.id)}
                  className={`flex flex-col items-center text-center gap-2 p-4 rounded-2xl border transition-all duration-200 ${
                    selected.includes(dt.id)
                      ? "bg-sky-500/10 border-sky-500/40 text-sky-300 shadow-inner shadow-sky-500/10"
                      : "border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200"
                  }`}
                >
                  <span className="text-xl">{dt.icon}</span>
                  <span className="text-xs font-semibold leading-tight">{dt.label}</span>
                </button>
              ))}
            </div>

            <div className="mt-5 flex items-center justify-between flex-wrap gap-3">
              <span className="text-xs text-slate-500">{selected.length} document type{selected.length !== 1 ? "s" : ""} selected</span>
              <button
                onClick={() => generateMutation.mutate()}
                disabled={selected.length === 0 || generateMutation.isLoading}
                className="bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white font-semibold py-2.5 px-6 rounded-xl text-sm transition-all shadow-lg shadow-sky-500/10 flex items-center gap-2 disabled:opacity-60"
              >
                {generateMutation.isLoading ? (
                  <><span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span> Generating...</>
                ) : "Generate Documentation"}
              </button>
            </div>
          </div>

          {/* Output */}
          {generated.length > 0 && (
            <div className="bg-slate-900 border border-slate-800 rounded-3xl shadow-xl overflow-hidden">
              {/* Tabs */}
              <div className="flex border-b border-slate-800 overflow-x-auto">
                {generated.map((doc) => {
                  const meta = DOC_TYPES.find((d) => d.id === doc.type);
                  return (
                    <button
                      key={doc.type}
                      onClick={() => setActiveTab(doc.type)}
                      className={`flex items-center gap-2 px-5 py-3 text-xs font-semibold whitespace-nowrap border-b-2 transition-all ${
                        activeTab === doc.type
                          ? "border-sky-500 text-sky-400"
                          : "border-transparent text-slate-400 hover:text-slate-200"
                      }`}
                    >
                      {meta?.icon} {meta?.label || doc.type}
                    </button>
                  );
                })}
              </div>

              {/* Content */}
              {activeDoc && (
                <div className="relative p-6">
                  <button
                    onClick={() => copyContent(activeDoc.type, activeDoc.content)}
                    className="absolute top-5 right-5 text-xs font-semibold text-slate-400 hover:text-slate-200 bg-slate-800 border border-slate-700 px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5"
                  >
                    {copied === activeDoc.type ? "✅ Copied!" : "📋 Copy"}
                  </button>
                  <pre className="text-sm text-slate-300 font-mono whitespace-pre-wrap leading-relaxed overflow-x-auto max-h-[500px] overflow-y-auto pr-20">
                    {activeDoc.content || "// No content generated."}
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
