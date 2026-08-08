import { useMemo, useState } from "react";
import { FileSearch, Files, Search } from "lucide-react";
import type { RepositoryFile } from "../../types/api";
import { FileTree } from "./FileTree";
import { Input } from "../ui/Input";
import { Card } from "../ui/Card";
import { EmptyState } from "../ui/EmptyState";
import { CodeViewer } from "../ui/CodeViewer";
import { NotebookViewer } from "../ui/NotebookViewer";
import { useRepositoryFileContent } from "../../hooks/useRepository";
import { baseName } from "../../lib/utils";

export interface FileExplorerProps {
  files: RepositoryFile[];
  repoId?: string;
  loading?: boolean;
  className?: string;
}

export function FileExplorer({ files, repoId, loading, className }: FileExplorerProps) {
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<string | null>(null);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return files;
    return files.filter((f) => f.file_path.toLowerCase().includes(q));
  }, [files, query]);

  const selectedFile = useMemo(
    () => files.find((f) => f.file_path === selected) ?? null,
    [files, selected]
  );

  const contentQuery = useRepositoryFileContent(repoId, selected);

  return (
    <div className={className}>
      <div className="mb-3 flex items-center gap-3">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-ink-3" />
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={`Search ${files.length} files…`}
            className="pl-9"
          />
        </div>
        <span className="flex items-center gap-1.5 text-2xs text-ink-3">
          <Files className="h-3 w-3" />
          {files.length} files
        </span>
      </div>

      <div className="grid gap-3 lg:grid-cols-[280px_1fr]">
        <Card className="scrollbar-thin max-h-[520px] overflow-y-auto p-1.5">
          {loading ? (
            <div className="space-y-1 p-1">
              {Array.from({ length: 14 }).map((_, i) => (
                <div key={i} className="skeleton h-7 rounded-md" style={{ marginLeft: (i % 4) * 14 }} />
              ))}
            </div>
          ) : filtered.length === 0 ? (
            <EmptyState
              icon={<FileSearch className="h-5 w-5" />}
              title={query ? "No matching files" : "No files indexed"}
              description={query ? "Try a different search term." : "Run the analysis to index the repository files."}
            />
          ) : (
            <FileTree files={filtered} activePath={selected ?? undefined} onSelect={setSelected} />
          )}
        </Card>

        <Card className="overflow-hidden">
          {selectedFile ? (
            <div className="flex h-[520px] flex-col">
              <div className="flex items-center justify-between gap-3 border-b border-line-1 bg-panel-1 px-4 py-3">
                <span className="flex items-center gap-2 font-mono text-xs text-ink-2">
                  <span className="h-2 w-2 rounded-full bg-line-3" aria-hidden />
                  {baseName(selectedFile.file_path)}
                </span>
                {selectedFile.language && (
                  <span className="text-2xs uppercase tracking-[0.08em] text-ink-3">{selectedFile.language}</span>
                )}
              </div>
              <div className="scrollbar-thin flex-1 overflow-auto">
                {contentQuery.isLoading ? (
                  <div className="space-y-1 p-4">
                    {Array.from({ length: 12 }).map((_, i) => (
                      <div key={i} className="skeleton h-4 rounded" style={{ width: `${(i % 4) * 20 + 40}%` }} />
                    ))}
                  </div>
                ) : contentQuery.error ? (
                  <EmptyState
                    icon={<FileSearch className="h-5 w-5" />}
                    title="Could not load file"
                    description={contentQuery.error instanceof Error ? contentQuery.error.message : "An error occurred."}
                  />
                ) : contentQuery.data?.data.content ? (
                  selectedFile.file_path.toLowerCase().endsWith(".ipynb") ? (
                    <NotebookViewer content={contentQuery.data.data.content} />
                  ) : (
                    <CodeViewer
                      code={contentQuery.data.data.content}
                      filename={selectedFile.file_path}
                      language={selectedFile.language ?? undefined}
                    />
                  )
                ) : (
                  <EmptyState
                    icon={<FileSearch className="h-5 w-5" />}
                    title="No content available"
                    description="This file could not be read. Ask QA Chat for questions about it."
                  />
                )}
              </div>
            </div>
          ) : (
            <div className="grid h-[520px] place-items-center">
              <EmptyState
                icon={<FileSearch className="h-5 w-5" />}
                title="Select a file to inspect"
                description="Choose a file from the tree to preview its raw content."
              />
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
