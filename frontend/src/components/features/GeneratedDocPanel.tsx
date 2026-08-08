import { useMemo, useState } from "react";
import { Check, Copy, Download, FileText } from "lucide-react";
import type { GeneratedDocument } from "../../types/api";
import { exportDocumentationPdf } from "../../services/repos";
import { Tabs } from "../ui/Tabs";
import { MarkdownViewer } from "../ui/MarkdownViewer";
import { IconButton } from "../ui/IconButton";
import { Tooltip } from "../ui/Tooltip";
import { slugify, titleCase } from "../../lib/utils";
import { useToast } from "../ui/Toast";

export interface GeneratedDocPanelProps {
  documents: GeneratedDocument[];
  repoId?: string;
  repoName?: string;
}

export function GeneratedDocPanel({ documents, repoId, repoName }: GeneratedDocPanelProps) {
  const { error: toastError } = useToast();
  const [active, setActive] = useState(0);
  const [copied, setCopied] = useState(false);
  const [downloading, setDownloading] = useState(false);

  const tabs = useMemo(
    () =>
      documents.map((doc) => ({
        id: doc.type,
        label: titleCase(doc.type).replace("_", " "),
      })),
    [documents]
  );

  const current = documents[Math.min(active, documents.length - 1)];

  const copy = async () => {
    if (!current) return;
    await navigator.clipboard.writeText(current.content);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1500);
  };

  const downloadPdf = async () => {
    if (!current || !repoId || downloading) return;
    const title = current.title ?? (repoName ? `${repoName} — ${current.type}` : "Documentation");
    setDownloading(true);
    try {
      const blob = await exportDocumentationPdf(repoId, title, current.content);
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `${slugify(title) || "documentation"}.pdf`;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      toastError(err instanceof Error ? err.message : "PDF download failed.");
    } finally {
      setDownloading(false);
    }
  };

  const activeTabId = tabs[Math.min(active, tabs.length - 1)]?.id ?? "";

  return (
    <div className="overflow-hidden rounded-xl2 border border-line-1 bg-panel-2">
      <div className="flex items-center justify-between gap-3 border-b border-line-1 px-4 py-2.5">
        <div className="min-w-0 flex-1">
          <Tabs tabs={tabs} active={activeTabId} onChange={(v) => setActive(tabs.findIndex((t) => t.id === v))} />
        </div>
        <div className="flex items-center gap-1.5">
          <Tooltip label="Copy markdown" side="bottom">
            <IconButton label="Copy markdown" onClick={copy}>
              {copied ? <Check className="h-4 w-4 text-success" /> : <Copy className="h-4 w-4" />}
            </IconButton>
          </Tooltip>
          <Tooltip label={downloading ? "Rendering PDF…" : "Download PDF"} side="bottom">
            <IconButton label="Download PDF" onClick={downloadPdf} disabled={downloading || !repoId}>
              <Download className={`h-4 w-4 ${downloading ? "animate-pulse" : ""}`} />
            </IconButton>
          </Tooltip>
        </div>
      </div>
      <div className="scrollbar-thin max-h-[560px] overflow-y-auto px-5 py-4">
        {current ? (
          <MarkdownViewer content={current.content} />
        ) : (
          <div className="flex items-center gap-2 text-sm text-ink-3">
            <FileText className="h-4 w-4" />
            No document generated.
          </div>
        )}
      </div>
    </div>
  );
}
