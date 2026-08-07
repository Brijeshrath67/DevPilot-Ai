import { useState, useRef, useEffect } from "react";
import { useParams } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import api from "../lib/api";
import Sidebar from "../components/common/Sidebar";
import Header from "../components/common/Header";

interface Message {
  id: number;
  sender: "user" | "assistant";
  text: string;
  provenance?: { id: string; file_path: string; score: number }[];
}

let msgCounter = 0;

export default function Chat() {
  const { repoId } = useParams();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 0,
      sender: "assistant",
      text: "👋 Hello! I'm your repository assistant. Ask me anything about this codebase — architecture, functions, file locations, or best practices.",
    },
  ]);
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const chatMutation = useMutation(
    async (question: string) => {
      const res = await api.post(`/repos/${repoId}/chat`, { question });
      return res.data;
    },
    {
      onSuccess: (data) => {
        const answer = data.data?.answer || "I couldn't find an answer in the current repository context.";
        const provenance = data.data?.provenance || [];
        setMessages((prev) => [
          ...prev,
          {
            id: ++msgCounter,
            sender: "assistant",
            text: answer,
            provenance,
          },
        ]);
      },
      onError: () => {
        setMessages((prev) => [
          ...prev,
          {
            id: ++msgCounter,
            sender: "assistant",
            text: "⚠️ Failed to get a response. Please ensure the repository has been analyzed first.",
          },
        ]);
      },
    }
  );

  const handleSend = () => {
    const q = input.trim();
    if (!q || chatMutation.isLoading) return;

    setMessages((prev) => [...prev, { id: ++msgCounter, sender: "user", text: q }]);
    setInput("");
    chatMutation.mutate(q);
  };

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header />
        <main className="flex-1 flex flex-col max-w-4xl w-full mx-auto p-6 gap-0">

          {/* Chat Header */}
          <div className="bg-slate-900 border border-slate-800 rounded-t-3xl px-6 py-4 flex items-center gap-3 border-b-0">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-violet-500 to-purple-600 flex items-center justify-center shadow-lg shadow-violet-500/20">
              <span className="text-base">💬</span>
            </div>
            <div>
              <h1 className="text-base font-bold text-white">Repository QA Chat</h1>
              <p className="text-[10px] text-slate-400">Powered by vector search + LLM context retrieval</p>
            </div>
            <div className="ml-auto flex items-center gap-1.5">
              <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
              <span className="text-xs text-emerald-400 font-medium">Online</span>
            </div>
          </div>

          {/* Messages Area */}
          <div className="flex-1 bg-slate-900 border border-slate-800 border-t-0 border-b-0 px-6 py-4 overflow-y-auto space-y-4 min-h-0 max-h-[calc(100vh-280px)]">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-3 ${msg.sender === "user" ? "flex-row-reverse" : "flex-row"}`}
              >
                {/* Avatar */}
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shrink-0 ${
                  msg.sender === "user"
                    ? "bg-slate-700 text-slate-300"
                    : "bg-gradient-to-tr from-violet-500 to-purple-600 text-white shadow shadow-violet-500/20"
                }`}>
                  {msg.sender === "user" ? "U" : "AI"}
                </div>

                {/* Bubble */}
                <div className={`max-w-[75%] space-y-1 ${msg.sender === "user" ? "items-end" : "items-start"} flex flex-col`}>
                  <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                    msg.sender === "user"
                      ? "bg-gradient-to-br from-sky-500 to-indigo-600 text-white rounded-tr-sm shadow-lg shadow-sky-500/10"
                      : "bg-slate-800 text-slate-200 border border-slate-700 rounded-tl-sm"
                  }`}>
                    {msg.text}
                  </div>

                  {/* Provenance Citations */}
                  {msg.provenance && msg.provenance.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {msg.provenance.slice(0, 4).map((p: any, i: number) => (
                        <span
                          key={i}
                          className="font-mono text-[9px] text-violet-400 bg-violet-500/10 border border-violet-500/20 px-2 py-0.5 rounded-full"
                        >
                          📄 {p.file_path || p.id}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {/* Typing Indicator */}
            {chatMutation.isLoading && (
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-violet-500 to-purple-600 flex items-center justify-center text-xs font-bold text-white shadow shadow-violet-500/20">AI</div>
                <div className="bg-slate-800 border border-slate-700 rounded-2xl rounded-tl-sm px-4 py-3 flex items-center gap-1">
                  <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:0ms]"></div>
                  <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:150ms]"></div>
                  <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:300ms]"></div>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input Row */}
          <div className="bg-slate-900 border border-slate-800 border-t-0 rounded-b-3xl px-4 py-4">
            <div className="flex items-end gap-3 bg-slate-950 border border-slate-800 rounded-2xl p-2">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKey}
                placeholder="Ask about this codebase... (Enter to send, Shift+Enter for newline)"
                rows={2}
                className="flex-1 resize-none bg-transparent text-sm text-slate-200 placeholder-slate-600 focus:outline-none px-2 py-1 leading-relaxed"
              />
              <button
                onClick={handleSend}
                disabled={!input.trim() || chatMutation.isLoading}
                className="shrink-0 w-10 h-10 rounded-xl bg-gradient-to-r from-violet-500 to-purple-600 hover:from-violet-400 hover:to-purple-500 disabled:opacity-40 flex items-center justify-center shadow-lg shadow-violet-500/10 transition-all"
              >
                <span className="text-base">➤</span>
              </button>
            </div>
            <p className="text-[10px] text-slate-600 text-center mt-2">
              Responses are grounded in your repository's code context.
            </p>
          </div>
        </main>
      </div>
    </div>
  );
}
