import { useMemo } from "react";
import type { ReactNode } from "react";
import { cn } from "../../lib/utils";

const KEYWORDS =
  /\b(def|class|return|import|from|as|if|elif|else|for|while|in|not|and|or|try|except|finally|raise|with|async|await|pass|yield|lambda|assert|del|global|nonlocal|True|False|None|break|continue|is)\b/;

function highlightLine(line: string): ReactNode[] {
  const tokens: ReactNode[] = [];
  const regex = /(#.*$)|("[^"]*"|'[^']*'|`[^`]*`)|(@[\w.]+)|(\b\d+(?:\.\d+)?\b)/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null;
  let key = 0;
  while ((match = regex.exec(line)) !== null) {
    const idx = match.index;
    if (idx > lastIndex) {
      tokens.push(<span key={key++}>{line.slice(lastIndex, idx)}</span>);
    }
    const [full, comment, str, decorator, num] = match;
    if (comment) tokens.push(<span key={key++} className="text-ink-3 italic">{comment}</span>);
    else if (str) tokens.push(<span key={key++} className="text-success">{str}</span>);
    else if (decorator) tokens.push(<span key={key++} className="text-accent2">{decorator}</span>);
    else if (num) tokens.push(<span key={key++} className="text-warning">{num}</span>);
    lastIndex = idx + full.length;
  }
  const rest = line.slice(lastIndex);
  if (rest) {
    const parts = rest.split(KEYWORDS);
    tokens.push(
      <span key={key}>
        {parts.map((part, i) =>
          i % 2 === 1 ? (
            <span key={i} className="text-accent">{part}</span>
          ) : (
            <span key={i}>{part}</span>
          )
        )}
      </span>
    );
  }
  return tokens;
}

export interface CodeViewerProps {
  code: string;
  filename?: string;
  language?: string;
  showLineNumbers?: boolean;
  className?: string;
  actions?: ReactNode;
}

export function CodeViewer({ code, filename, language, showLineNumbers = true, className, actions }: CodeViewerProps) {
  const lines = useMemo(() => code.replace(/\n$/, "").split("\n"), [code]);

  return (
    <div className={cn("overflow-hidden rounded-xl2 border border-line-1 bg-[#0b0b10]", className)}>
      {(filename || actions) && (
        <div className="flex items-center justify-between border-b border-line-1 bg-panel-1 px-4 py-2.5">
          <div className="flex items-center gap-2">
            {filename && (
              <span className="flex items-center gap-2 font-mono text-xs text-ink-2">
                <span className="h-2 w-2 rounded-full bg-line-3" aria-hidden />
                {filename}
              </span>
            )}
            {language && <span className="text-2xs uppercase tracking-[0.08em] text-ink-3">{language}</span>}
          </div>
          {actions}
        </div>
      )}
      <div className="scrollbar-thin overflow-x-auto">
        <table className="w-full border-collapse font-mono text-[12.5px] leading-relaxed">
          <tbody>
            {lines.map((line, i) => (
              <tr key={i} className="hover:bg-white/[0.02]">
                {showLineNumbers && (
                  <td className="select-none border-r border-line-1 px-3 py-0 text-right align-top text-ink-3/60">
                    {i + 1}
                  </td>
                )}
                <td className="whitespace-pre px-4 py-0 text-slate-200">
                  {highlightLine(line)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
