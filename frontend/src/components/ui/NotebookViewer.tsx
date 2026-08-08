import { useMemo } from "react";
import { NotebookText } from "lucide-react";
import { cn } from "../../lib/utils";
import { CodeViewer } from "./CodeViewer";
import { MarkdownViewer } from "./MarkdownViewer";

interface NotebookCell {
  cell_type: string;
  source?: string[] | string;
}

export interface NotebookViewerProps {
  content: string;
  className?: string;
}

function cellSource(cell: NotebookCell): string {
  const source = cell.source;
  if (Array.isArray(source)) return source.join("");
  return source ?? "";
}

function parseNotebook(content: string): { cells: NotebookCell[]; error?: string } {
  try {
    const data = JSON.parse(content);
    if (!data || typeof data !== "object" || !Array.isArray(data.cells)) {
      return { cells: [], error: "Not a valid Jupyter notebook (missing cells)." };
    }
    return { cells: data.cells as NotebookCell[] };
  } catch {
    return { cells: [], error: "Could not parse notebook JSON." };
  }
}

export function NotebookViewer({ content, className }: NotebookViewerProps) {
  const { cells, error } = useMemo(() => parseNotebook(content), [content]);

  if (error) {
    return (
      <div className="grid h-full place-items-center p-6">
        <div className="text-center">
          <NotebookText className="mx-auto mb-2 h-6 w-6 text-warning" />
          <p className="text-xs text-ink-3">{error}</p>
        </div>
      </div>
    );
  }

  if (cells.length === 0) {
    return (
      <div className="grid h-full place-items-center p-6">
        <p className="text-xs text-ink-3">Notebook is empty.</p>
      </div>
    );
  }

  return (
    <div className={cn("space-y-3 p-4", className)}>
      {cells.map((cell, index) =>
        cell.cell_type === "markdown" ? (
          <div key={index} className="rounded-xl border border-line-1 bg-panel-1 px-4 py-3">
            <MarkdownViewer content={cellSource(cell)} />
          </div>
        ) : (
          <CodeViewer key={index} code={cellSource(cell)} showLineNumbers={false} />
        )
      )}
    </div>
  );
}
