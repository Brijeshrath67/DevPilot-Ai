import { useEffect, useMemo, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { Bot, FileText, MessageSquarePlus, MessagesSquare, Send, Sparkles, User } from "lucide-react";
import { PageHeader } from "../components/features/PageHeader";
import { AnalyzeGate } from "../components/features/AnalyzeGate";
import { RepoStatusBadge } from "../components/repository/RepoStatusBadge";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { Textarea } from "../components/ui/Input";
import { SkeletonLines } from "../components/ui/Skeleton";
import { useRepository } from "../hooks/useRepository";
import { useRepoStatus, isProcessing } from "../hooks/useRepoStatus";
import { useChat } from "../hooks/useFeatureActions";
import { useToast } from "../components/ui/Toast";
import { cn, timeAgo } from "../lib/utils";

interface ChatMessageItem {
  role: "user" | "assistant";
  content: string;
  provenance?: string[];
  mode?: "grounded" | "open";
  at: number;
  error?: boolean;
}

interface ChatSessionItem {
  id: string;
  title: string;
  createdAt: number;
  messages: ChatMessageItem[];
}

function loadSessions(repoId: string): ChatSessionItem[] {
  try {
    const raw = localStorage.getItem(`devpilot-chat-${repoId}`);
    return raw ? (JSON.parse(raw) as ChatSessionItem[]) : [];
  } catch {
    return [];
  }
}

function newSessionId(): string {
  return `sess_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

function sessionTitle(question: string): string {
  return question.length > 42 ? `${question.slice(0, 42)}…` : question;
}

export function QAChatPage() {
  const { repoId } = useParams();
  const { error: toastError } = useToast();
  const repoQuery = useRepository(repoId);
  const { status, isLoading: statusLoading } = useRepoStatus(repoId);
  const chat = useChat(repoId);

  const [sessions, setSessions] = useState<ChatSessionItem[]>(() =>
    repoId ? loadSessions(repoId) : []
  );
  const [activeId, setActiveId] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const [waiting, setWaiting] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const repo = repoQuery.data?.data;
  const loading = repoQuery.isLoading || statusLoading;

  useEffect(() => {
    if (!repoId) return;
    setSessions(loadSessions(repoId));
    setActiveId(null);
  }, [repoId]);

  useEffect(() => {
    if (!repoId) return;
    localStorage.setItem(`devpilot-chat-${repoId}`, JSON.stringify(sessions));
  }, [sessions, repoId]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [sessions, waiting]);

  const active = useMemo(
    () => sessions.find((s) => s.id === activeId) ?? null,
    [sessions, activeId]
  );

  const startNew = () => {
    const session: ChatSessionItem = {
      id: newSessionId(),
      title: "New conversation",
      createdAt: Date.now(),
      messages: [],
    };
    setSessions((prev) => [session, ...prev]);
    setActiveId(session.id);
  };

  useEffect(() => {
    if (sessions.length === 0 && repoId) startNew();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [repoId]);

  const send = async () => {
    const question = input.trim();
    if (!question || waiting || !activeId) return;
    setInput("");
    setWaiting(true);

    const userMessage: ChatMessageItem = { role: "user", content: question, at: Date.now() };
    setSessions((prev) =>
      prev.map((s) =>
        s.id === activeId
          ? {
              ...s,
              title: s.messages.length === 0 ? sessionTitle(question) : s.title,
              messages: [...s.messages, userMessage],
            }
          : s
      )
    );

    try {
      const res = await chat.mutateAsync({ question, sessionId: activeId });
      const assistant: ChatMessageItem = {
        role: "assistant",
        content: res.data.answer,
        provenance: res.data.provenance,
        mode: res.data.mode ?? "open",
        at: Date.now(),
      };
      setSessions((prev) =>
        prev.map((s) => (s.id === activeId ? { ...s, messages: [...s.messages, assistant] } : s))
      );
    } catch (err) {
      const message = err instanceof Error ? err.message : "Chat request failed.";
      toastError(message);
      setSessions((prev) =>
        prev.map((s) =>
          s.id === activeId
            ? {
                ...s,
                messages: [
                  ...s.messages,
                  { role: "assistant", content: `Something went wrong: ${message}`, at: Date.now(), error: true },
                ],
              }
            : s
        )
      );
    } finally {
      setWaiting(false);
    }
  };

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void send();
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="QA chat"
        description="Ask questions about the workspace — answers are grounded in the indexed codebase with source citations."
        icon={<MessagesSquare className="h-5 w-5" />}
        badge={repo ? <RepoStatusBadge status={status ?? repo.status} /> : undefined}
        actions={
          <Button size="sm" variant="secondary" icon={<MessageSquarePlus className="h-3.5 w-3.5" />} onClick={startNew}>
            New chat
          </Button>
        }
      />

      {loading ? (
        <Card className="p-5">
          <SkeletonLines lines={5} />
        </Card>
      ) : !repo ? (
        <Card className="p-4">
          <p className="py-10 text-center text-sm text-ink-3">Repository not found.</p>
        </Card>
      ) : isProcessing(status) ? (
        <Card className="p-5">
          <p className="py-8 text-center text-sm text-ink-3">Workspace is still being analyzed — wait for analysis to finish.</p>
        </Card>
      ) : status !== "analyzed" ? (
        <AnalyzeGate repoId={repoId!} />
      ) : (
        <Card className="grid h-[calc(100vh-220px)] min-h-[440px] overflow-hidden lg:grid-cols-[220px_1fr]">
          <div className="hidden flex-col border-r border-line-1 bg-panel-1 lg:flex">
            <div className="border-b border-line-1 p-3">
              <Button size="sm" variant="secondary" className="w-full" icon={<MessageSquarePlus className="h-3.5 w-3.5" />} onClick={startNew}>
                New chat
              </Button>
            </div>
            <div className="scrollbar-thin flex-1 space-y-0.5 overflow-y-auto p-2">
              {sessions.map((session) => (
                <button
                  key={session.id}
                  onClick={() => setActiveId(session.id)}
                  className={cn(
                    "w-full truncate rounded-lg px-3 py-2 text-left text-xs transition-colors",
                    session.id === activeId
                      ? "bg-accent/10 font-medium text-accent"
                      : "text-ink-3 hover:bg-panel-3 hover:text-ink-2"
                  )}
                >
                  <span className="block truncate">{session.title}</span>
                  <span className="mt-0.5 block text-2xs text-ink-3/70">{timeAgo(session.createdAt)}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="flex min-w-0 flex-col">
            <div ref={scrollRef} className="scrollbar-thin flex-1 overflow-y-auto">
              {active && active.messages.length === 0 ? (
                <div className="flex h-full flex-col items-center justify-center gap-3 px-6 text-center">
                  <div className="grid h-12 w-12 place-items-center rounded-xl bg-accent/10 text-accent">
                    <Sparkles className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-ink">Ask about your codebase</p>
                    <p className="mx-auto mt-1 max-w-sm text-xs leading-relaxed text-ink-3">
                      Example: “What does this repository do?” or “How is authentication handled?”
                    </p>
                  </div>
                </div>
              ) : (
                <div className="space-y-5 px-4 py-5 sm:px-6">
                  {active?.messages.map((message, index) => (
                    <div key={index} className={cn("flex gap-3", message.role === "user" && "flex-row-reverse")}>
                      <div
                        className={cn(
                          "grid h-7 w-7 shrink-0 place-items-center rounded-lg border",
                          message.role === "user"
                            ? "border-line-2 bg-panel-3 text-ink-2"
                            : "border-accent/25 bg-accent/10 text-accent"
                        )}
                      >
                        {message.role === "user" ? <User className="h-3.5 w-3.5" /> : <Bot className="h-3.5 w-3.5" />}
                      </div>
                      <div className={cn("min-w-0 max-w-[82%]", message.role === "user" ? "text-right" : "text-left")}>
                        <div
                          className={cn(
                            "inline-block rounded-2xl border px-4 py-3 text-left text-[13px] leading-relaxed",
                            message.role === "user"
                              ? "border-accent/25 bg-accent/10 text-ink"
                              : "border-line-1 bg-panel-1 text-ink-2",
                            message.error && "border-critical/25 text-critical"
                          )}
                        >
                          {message.content}
                        </div>
                        {(message.mode || message.provenance?.length) && (
                          <div className="mt-2 flex flex-wrap items-center justify-end gap-1.5">
                            {message.mode && message.mode === "grounded" ? (
                              <span className="inline-flex items-center gap-1 rounded-md border border-success/25 bg-success/10 px-1.5 py-0.5 text-2xs font-medium text-success">
                                Grounded in repo
                              </span>
                            ) : message.mode === "open" ? (
                              <span className="inline-flex items-center gap-1 rounded-md border border-info/25 bg-info/10 px-1.5 py-0.5 text-2xs font-medium text-info">
                                Open answer
                              </span>
                            ) : null}
                            {message.provenance?.slice(0, 6).map((file, i) => (
                              <span
                                key={i}
                                title={file}
                                className="inline-flex max-w-[220px] items-center gap-1 truncate rounded-md border border-line-1 bg-panel-2 px-2 py-1 font-mono text-2xs text-ink-3"
                              >
                                <FileText className="h-3 w-3 shrink-0" />
                                <span className="truncate">{file}</span>
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                  {waiting && (
                    <div className="flex gap-3">
                      <div className="grid h-7 w-7 shrink-0 place-items-center rounded-lg border border-accent/25 bg-accent/10 text-accent">
                        <Bot className="h-3.5 w-3.5" />
                      </div>
                      <div className="flex items-center gap-1 rounded-2xl border border-line-1 bg-panel-1 px-4 py-3">
                        {[0, 1, 2].map((dot) => (
                          <span
                            key={dot}
                            className="h-1.5 w-1.5 animate-dot-bounce rounded-full bg-accent"
                            style={{ animationDelay: `${dot * 0.15}s` }}
                          />
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            <div className="border-t border-line-1 p-3 sm:p-4">
              <div className="relative">
                <Textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={onKeyDown}
                  placeholder="Ask a question about the repository…"
                  rows={1}
                  className="max-h-40 min-h-11 resize-none py-3 pl-4 pr-12"
                />
                <button
                  onClick={() => void send()}
                  disabled={!input.trim() || waiting}
                  aria-label="Send message"
                  className={cn(
                    "absolute bottom-2.5 right-2.5 grid h-7 w-7 place-items-center rounded-lg transition-all",
                    input.trim() && !waiting
                      ? "bg-accent text-white hover:brightness-110"
                      : "bg-panel-3 text-ink-3"
                  )}
                >
                  <Send className="h-3.5 w-3.5" />
                </button>
              </div>
              <p className="mt-2 text-2xs text-ink-3">
                Enter to send · Shift+Enter for a new line · answers cite source files
              </p>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
