import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { FileArchive, FolderGit2, Link2, UploadCloud } from "lucide-react";
import { Modal } from "../ui/Modal";
import { Button } from "../ui/Button";
import { Field, Input } from "../ui/Input";
import { SegmentedControl } from "../ui/SegmentedControl";
import { useToast } from "../ui/Toast";
import { uploadRepository } from "../../services/repos";
import { formatBytes } from "../../lib/utils";

type SourceMode = "github_url" | "archive";

export interface NewRepositoryModalProps {
  open: boolean;
  onClose: () => void;
}

export function NewRepositoryModal({ open, onClose }: NewRepositoryModalProps) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { success: toastSuccess, error: toastError } = useToast();

  const [mode, setMode] = useState<SourceMode>("github_url");
  const [url, setUrl] = useState("");
  const [name, setName] = useState("");
  const [archive, setArchive] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const reset = () => {
    setUrl("");
    setName("");
    setArchive(null);
    setDragging(false);
  };

  const close = () => {
    onClose();
    window.setTimeout(reset, 250);
  };

  const valid = mode === "github_url" ? url.trim().length > 0 : Boolean(archive);

  const submit = async () => {
    if (!valid || submitting) return;
    setSubmitting(true);
    try {
      const res = await uploadRepository({
        sourceType: mode,
        sourceValue: mode === "github_url" ? url.trim() : undefined,
        repositoryName: name.trim() || undefined,
        archive: mode === "archive" ? archive ?? undefined : undefined,
      });
      queryClient.invalidateQueries({ queryKey: ["repositories"] });
      toastSuccess(`Repository “${res.data.name}” created — ingesting files…`);
      close();
      navigate(`/repo/${res.data.repository_id}`);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to create repository.";
      toastError(message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal open={open} onClose={onClose} title="Import a repository" description="Ingest a GitHub repository or a ZIP archive to start working with DevPilot.">
      <div className="space-y-4 p-5">
        <SegmentedControl<SourceMode>
          ariaLabel="Import source"
          value={mode}
          onChange={(m) => setMode(m)}
          options={[
            { value: "github_url", label: <span className="flex items-center gap-1.5"><Link2 className="h-3 w-3" />GitHub URL</span> },
            { value: "archive", label: <span className="flex items-center gap-1.5"><FolderGit2 className="h-3 w-3" />ZIP upload</span> },
          ]}
        />

        {mode === "github_url" ? (
          <div className="space-y-3">
            <Field label="Repository URL" hint="e.g. https://github.com/facebook/react">
              <Input
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://github.com/owner/repository"
                autoFocus
              />
            </Field>
            <Field label="Workspace name (optional)">
              <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Auto-derived from the URL" />
            </Field>
          </div>
        ) : (
          <div className="space-y-3">
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              onDragOver={(e) => {
                e.preventDefault();
                setDragging(true);
              }}
              onDragLeave={() => setDragging(false)}
              onDrop={(e) => {
                e.preventDefault();
                setDragging(false);
                const file = e.dataTransfer.files?.[0];
                if (file) setArchive(file);
              }}
              className={`flex w-full flex-col items-center justify-center gap-2 rounded-xl border border-dashed px-6 py-8 text-center transition-colors ${
                dragging ? "border-accent bg-accent/5" : "border-line-2 hover:border-line-3"
              }`}
            >
              <span className="grid h-10 w-10 place-items-center rounded-xl bg-accent/10 text-accent">
                <UploadCloud className="h-5 w-5" />
              </span>
              {archive ? (
                <>
                  <span className="flex items-center gap-1.5 text-sm font-medium text-ink">
                    <FileArchive className="h-4 w-4" />
                    {archive.name}
                  </span>
                  <span className="text-2xs text-ink-3">{formatBytes(archive.size)} — click to replace</span>
                </>
              ) : (
                <>
                  <span className="text-sm font-medium text-ink">Drop a ZIP archive here</span>
                  <span className="text-2xs text-ink-3">or click to browse your files</span>
                </>
              )}
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept=".zip,application/zip"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) setArchive(file);
              }}
            />
            <Field label="Workspace name (optional)">
              <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Auto-derived from the archive" />
            </Field>
          </div>
        )}

        <div className="flex justify-end gap-2 border-t border-line-1 pt-4">
          <Button variant="ghost" onClick={close}>
            Cancel
          </Button>
          <Button onClick={submit} loading={submitting} disabled={!valid} icon={<FolderGit2 className="h-4 w-4" />}>
            Create workspace
          </Button>
        </div>
      </div>
    </Modal>
  );
}
