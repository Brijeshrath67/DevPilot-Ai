import { Fragment, useMemo } from "react";
import type { ReactNode } from "react";
import { cn } from "../../lib/utils";

function escapeHtml(text: string): string {
  return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function renderInline(text: string): ReactNode[] {
  const nodes: ReactNode[] = [];
  const regex = /(`[^`]+`)|(\*\*[^*]+\*\*)|(\*[^*]+\*)|(\[[^\]]+\]\([^)]+\))/g;
  let last = 0;
  let match: RegExpExecArray | null;
  let key = 0;
  while ((match = regex.exec(text)) !== null) {
    const idx = match.index;
    if (idx > last) nodes.push(<Fragment key={key++}>{escapeHtml(text.slice(last, idx))}</Fragment>);
    const [full, code, bold, italic, link] = match;
    if (code) {
      nodes.push(
        <code key={key++} className="rounded bg-panel-3 px-1.5 py-0.5 font-mono text-[0.9em] text-info">
          {escapeHtml(code.slice(1, -1))}
        </code>
      );
    } else if (bold) {
      nodes.push(<strong key={key++} className="font-semibold text-ink">{escapeHtml(bold.slice(2, -2))}</strong>);
    } else if (italic) {
      nodes.push(<em key={key++} className="italic">{escapeHtml(italic.slice(1, -1))}</em>);
    } else if (link) {
      const labelMatch = full.match(/\[([^\]]+)\]/);
      const hrefMatch = full.match(/\(([^)]+)\)/);
      const label = labelMatch ? labelMatch[1] : full;
      const href = hrefMatch ? hrefMatch[1] : "#";
      nodes.push(
        <a
          key={key++}
          href={href}
          target="_blank"
          rel="noreferrer noopener"
          className="text-accent underline decoration-accent/30 underline-offset-2 hover:decoration-accent"
        >
          {escapeHtml(label)}
        </a>
      );
    }
    last = idx + full.length;
  }
  if (last < text.length) nodes.push(<Fragment key={key}>{escapeHtml(text.slice(last))}</Fragment>);
  return nodes;
}

interface Block {
  kind: string;
  content?: string;
  items?: string[];
}

function parseBlocks(source: string): Block[] {
  const lines = source.split("\n");
  const blocks: Block[] = [];
  let i = 0;
  const pushText = (kind: string, text: string) => {
    if (!text.trim()) return;
    blocks.push({ kind, content: text.trim() });
  };
  while (i < lines.length) {
    const line = lines[i];
    if (line.trim() === "") {
      i += 1;
      continue;
    }
    if (line.trim().startsWith("```")) {
      const code: string[] = [];
      i += 1;
      while (i < lines.length && !lines[i].trim().startsWith("```")) {
        code.push(lines[i]);
        i += 1;
      }
      i += 1; // skip closing fence
      blocks.push({ kind: "code", content: code.join("\n") });
      continue;
    }
    const heading = line.match(/^(#{1,6})\s+(.*)$/);
    if (heading) {
      pushText(`h${heading[1].length}`, heading[2]);
      i += 1;
      continue;
    }
    if (/^\s*(?:[-*_])\s*$/.test(line.trim())) {
      blocks.push({ kind: "hr", content: "" });
      i += 1;
      continue;
    }
    const listStart = line.match(/^\s*[-*+]\s+/);
    const olStart = line.match(/^\s*\d+[.)]\s+/);
    if (listStart || olStart) {
      const items: string[] = [];
      const ordered = Boolean(olStart);
      while (i < lines.length) {
        const match = lines[i].match(ordered ? /^\s*\d+[.)]\s+(.*)$/ : /^\s*[-*+]\s+(.*)$/);
        if (!match) break;
        items.push(match[1]);
        i += 1;
      }
      blocks.push({ kind: ordered ? "ol" : "ul", items });
      continue;
    }
    if (line.trim().startsWith("> ")) {
      const quote: string[] = [];
      while (i < lines.length && lines[i].trim().startsWith(">")) {
        quote.push(lines[i].trim().replace(/^>\s?/, ""));
        i += 1;
      }
      blocks.push({ kind: "quote", content: quote.join(" ") });
      continue;
    }
    pushText("p", line);
    i += 1;
  }
  return blocks;
}

export interface MarkdownViewerProps {
  content: string;
  className?: string;
}

export function MarkdownViewer({ content, className }: MarkdownViewerProps) {
  const blocks = useMemo(() => parseBlocks(content), [content]);

  return (
    <div className={cn("space-y-3 text-sm leading-relaxed text-ink-2", className)}>
      {blocks.map((block, index) => {
        switch (block.kind) {
          case "h1":
            return <h1 key={index} className="border-b border-line-1 pb-2 text-2xl font-semibold tracking-tight text-ink">{renderInline(block.content ?? "")}</h1>;
          case "h2":
            return <h2 key={index} className="pt-2 text-xl font-semibold tracking-tight text-ink">{renderInline(block.content ?? "")}</h2>;
          case "h3":
            return <h3 key={index} className="pt-1 text-base font-semibold text-ink">{renderInline(block.content ?? "")}</h3>;
          case "h4":
          case "h5":
          case "h6":
            return <h4 key={index} className="text-sm font-semibold text-ink">{renderInline(block.content ?? "")}</h4>;
          case "p":
            return <p key={index}>{renderInline(block.content ?? "")}</p>;
          case "code":
            return (
              <pre key={index} className="scrollbar-thin overflow-x-auto rounded-lg border border-line-1 bg-[#0b0b10] p-3 font-mono text-[12.5px] leading-relaxed text-slate-200">
                {block.content}
              </pre>
            );
          case "ul":
            return (
              <ul key={index} className="space-y-1 pl-1">
                {block.items!.map((item, j) => (
                  <li key={j} className="flex gap-2">
                    <span className="mt-0.5 text-accent">›</span>
                    <span>{renderInline(item)}</span>
                  </li>
                ))}
              </ul>
            );
          case "ol":
            return (
              <ol key={index} className="list-decimal space-y-1 pl-5 marker:text-ink-3">
                {block.items!.map((item, j) => (
                  <li key={j}>{renderInline(item)}</li>
                ))}
              </ol>
            );
          case "quote":
            return (
              <blockquote key={index} className="border-l-2 border-accent/40 pl-3 text-ink-3">
                {renderInline(block.content ?? "")}
              </blockquote>
            );
          case "hr":
            return <hr key={index} className="border-line-2" />;
          default:
            return null;
        }
      })}
    </div>
  );
}
