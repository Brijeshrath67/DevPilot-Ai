import { useMemo, useState } from "react";
import type { ReactNode } from "react";
import {
  Braces,
  ChevronDown,
  ChevronRight,
  Database,
  File,
  FileCode2,
  FileJson,
  FileText,
  Folder,
  FolderOpen,
  Globe,
  Image,
  NotebookText,
  Package,
  TerminalSquare,
} from "lucide-react";
import type { RepositoryFile } from "../../types/api";
import { cn } from "../../lib/utils";

interface TreeNode {
  name: string;
  path: string;
  type: "dir" | "file";
  language?: string | null;
  children: Map<string, TreeNode>;
}

function buildTree(files: RepositoryFile[]): TreeNode {
  const root: TreeNode = { name: "", path: "", type: "dir", children: new Map() };
  for (const file of files) {
    const parts = file.file_path.split("/");
    let node = root;
    let acc = "";
    for (let i = 0; i < parts.length; i += 1) {
      acc = acc ? `${acc}/${parts[i]}` : parts[i];
      const isLast = i === parts.length - 1;
      if (!node.children.has(parts[i])) {
        node.children.set(parts[i], {
          name: parts[i],
          path: acc,
          type: isLast ? "file" : "dir",
          language: isLast ? file.language : null,
          children: new Map(),
        });
      }
      node = node.children.get(parts[i])!;
    }
  }
  return root;
}

function fileIcon(name: string, language?: string | null) {
  const lang = (language ?? "").toLowerCase();
  const ext = name.split(".").pop()?.toLowerCase();
  if (["jupyter notebook", "ipynb"].includes(lang) || ext === "ipynb")
    return <NotebookText className="h-3.5 w-3.5 text-accent2" />;
  if (["python", "py"].includes(lang)) return <FileCode2 className="h-3.5 w-3.5 text-info" />;
  if (["typescript", "ts", "tsx"].includes(lang) || ["ts", "tsx"].includes(ext ?? ""))
    return <FileCode2 className="h-3.5 w-3.5 text-accent" />;
  if (["javascript", "js", "jsx"].includes(lang) || ["js", "jsx"].includes(ext ?? ""))
    return <Braces className="h-3.5 w-3.5 text-warning" />;
  if (["json", "yaml", "yml", "toml"].includes(ext ?? "")) return <FileJson className="h-3.5 w-3.5 text-warning" />;
  if (["md", "markdown", "txt"].includes(ext ?? "")) return <FileText className="h-3.5 w-3.5 text-ink-3" />;
  if (["png", "jpg", "jpeg", "svg", "gif", "webp"].includes(ext ?? "")) return <Image className="h-3.5 w-3.5 text-success" />;
  if (["sql", "db", "sqlite"].includes(ext ?? "")) return <Database className="h-3.5 w-3.5 text-warning" />;
  if (["html", "css", "scss", "less"].includes(ext ?? "")) return <Globe className="h-3.5 w-3.5 text-info" />;
  if (["sh", "bash", "zsh", "bat"].includes(ext ?? "")) return <TerminalSquare className="h-3.5 w-3.5 text-ink-3" />;
  if (name.includes("package") || ["pyproject", "cargo", "go.mod"].some((n) => name.includes(n)))
    return <Package className="h-3.5 w-3.5 text-accent" />;
  return <File className="h-3.5 w-3.5 text-ink-3" />;
}

export interface FileTreeProps {
  files: RepositoryFile[];
  activePath?: string | null;
  onSelect?: (path: string) => void;
  className?: string;
}

export function FileTree({ files, activePath, onSelect, className }: FileTreeProps) {
  const root = useMemo(() => buildTree(files), [files]);
  const [expanded, setExpanded] = useState<Set<string>>(
    () => new Set(Array.from(root.children.values()).filter((n) => n.type === "dir").map((n) => n.path))
  );

  const toggle = (path: string) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(path)) next.delete(path);
      else next.add(path);
      return next;
    });
  };

  const renderNode = (node: TreeNode, depth: number): ReactNode => {
    const pad = { paddingLeft: `${depth * 14 + 8}px` };
    if (node.type === "dir") {
      const open = expanded.has(node.path);
      return (
        <div key={node.path}>
          <button
            onClick={() => toggle(node.path)}
            style={pad}
            className="flex w-full items-center gap-1.5 rounded-md px-2 py-1.5 text-xs font-medium text-ink-2 transition-colors hover:bg-panel-3 hover:text-ink"
          >
            {open ? <ChevronDown className="h-3 w-3 shrink-0 text-ink-3" /> : <ChevronRight className="h-3 w-3 shrink-0 text-ink-3" />}
            {open ? <FolderOpen className="h-3.5 w-3.5 shrink-0 text-accent" /> : <Folder className="h-3.5 w-3.5 shrink-0 text-ink-3" />}
            <span className="truncate">{node.name}</span>
            <span className="ml-auto text-2xs text-ink-3/70">{node.children.size}</span>
          </button>
          {open && (
            <div className="animate-fade-in">
              {Array.from(node.children.values()).map((child) => renderNode(child, depth + 1))}
            </div>
          )}
        </div>
      );
    }
    const active = node.path === activePath;
    return (
      <button
        key={node.path}
        onClick={() => onSelect?.(node.path)}
        style={pad}
        title={node.path}
        className={cn(
          "flex w-full items-center gap-1.5 rounded-md px-2 py-1.5 text-xs transition-colors",
          active
            ? "bg-accent/10 font-medium text-accent"
            : "text-ink-3 hover:bg-panel-3 hover:text-ink-2"
        )}
      >
        {fileIcon(node.name, node.language)}
        <span className="truncate">{node.name}</span>
      </button>
    );
  };

  return (
    <div className={cn("space-y-0.5", className)} role="tree" aria-label="File tree">
      {Array.from(root.children.values()).map((child) => renderNode(child, 0))}
    </div>
  );
}
