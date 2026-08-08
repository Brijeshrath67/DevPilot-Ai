import { useEffect } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { getRepository, getRepositoryStatus } from "../services/repos";

const POLL_INTERVAL = 3000;
const ACTIVE_STATUSES = new Set(["pending", "analyzing"]);

export function useRepoStatus(repoId: string | undefined) {
  const queryClient = useQueryClient();
  const statusQuery = useQuery({
    queryKey: ["repo-status", repoId],
    queryFn: () => getRepositoryStatus(repoId!),
    enabled: Boolean(repoId),
  });

  const status = statusQuery.data?.data.status;
  const active = Boolean(status && ACTIVE_STATUSES.has(status));

  useEffect(() => {
    if (!repoId || !active) return;
    const id = window.setInterval(async () => {
      try {
        const [statusRes, detailRes] = await Promise.all([
          getRepositoryStatus(repoId),
          getRepository(repoId),
        ]);
        queryClient.setQueryData(["repo-status", repoId], statusRes);
        queryClient.setQueryData(["repo", repoId], detailRes);
      } catch {
        // transient polling error — ignore and retry on next tick
      }
    }, POLL_INTERVAL);
    return () => window.clearInterval(id);
  }, [active, repoId, queryClient]);

  return {
    status,
    isLoading: statusQuery.isLoading,
  };
}

export function isProcessing(status?: string): boolean {
  return Boolean(status && ACTIVE_STATUSES.has(status));
}
