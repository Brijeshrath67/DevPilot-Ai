import { useState } from "react";
import Sidebar from "../components/common/Sidebar";
import Header from "../components/common/Header";

export default function Settings() {
  const [apiKey, setApiKey] = useState("");
  const [apiUrl, setApiUrl] = useState("https://api.openai.com/v1");
  const [backendUrl, setBackendUrl] = useState("http://localhost:8000/api/v1");
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    localStorage.setItem("devpilot_api_key", apiKey);
    localStorage.setItem("devpilot_api_url", apiUrl);
    localStorage.setItem("devpilot_backend_url", backendUrl);
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header />
        <main className="flex-1 p-8 max-w-2xl w-full mx-auto space-y-6">

          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-7 shadow-xl">
            <h1 className="text-2xl font-extrabold text-white flex items-center gap-3">⚙️ Settings</h1>
            <p className="text-sm text-slate-400 mt-2">Configure your DevPilot AI workspace preferences.</p>
          </div>

          <form onSubmit={handleSave} className="space-y-4">
            {/* AI Configuration */}
            <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-5">
              <div>
                <h2 className="text-sm font-bold text-white">AI API Configuration</h2>
                <p className="text-xs text-slate-400 mt-0.5">Connect to Groq, Hugging Face, Mistral, NVIDIA, OpenRouter, Cerebras, or a compatible endpoint.</p>
              </div>
              <div className="space-y-1">
                <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">API Key</label>
                <input
                  type="password"
                  placeholder="sk-... or your provider API key"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-sky-500 transition-colors font-mono"
                />
              </div>
              <div className="space-y-1">
                <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">API Base URL</label>
                <input
                  type="url"
                  value={apiUrl}
                  onChange={(e) => setApiUrl(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-sky-500 transition-colors"
                />
              </div>
            </div>

            {/* Backend Configuration */}
            <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-5">
              <div>
                <h2 className="text-sm font-bold text-white">Backend Configuration</h2>
                <p className="text-xs text-slate-400 mt-0.5">Point the frontend to your FastAPI deployment.</p>
              </div>
              <div className="space-y-1">
                <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Backend API URL</label>
                <input
                  type="url"
                  value={backendUrl}
                  onChange={(e) => setBackendUrl(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-sky-500 transition-colors"
                />
              </div>
            </div>

            {/* About */}
            <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-3">
              <h2 className="text-sm font-bold text-white">About DevPilot AI</h2>
              <div className="grid grid-cols-2 gap-2 text-xs text-slate-400">
                {[
                  ["Version", "v0.1.0"],
                  ["Frontend", "React + Vite + TailwindCSS"],
                  ["Backend", "FastAPI + Python 3.12"],
                  ["Database", "MongoDB Atlas (SQLite fallback)"],
                  ["Vector Store", "Pinecone (local fallback)"],
                  ["AI Engine", "Multi-provider (Groq / HF / Mistral / NVIDIA / OpenRouter / Cerebras)"],
                  ["License", "MIT"],
                ].map(([label, value]) => (
                  <div key={label} className="flex flex-col">
                    <span className="text-[10px] uppercase font-bold tracking-wider text-slate-500">{label}</span>
                    <span className="text-slate-300 font-mono text-xs">{value}</span>
                  </div>
                ))}
              </div>
            </div>

            <button
              type="submit"
              className="w-full bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white font-semibold py-3 rounded-xl text-sm transition-all shadow-lg shadow-sky-500/10 flex items-center justify-center gap-2"
            >
              {saved ? "✅ Saved Successfully!" : "Save Settings"}
            </button>
          </form>
        </main>
      </div>
    </div>
  );
}
