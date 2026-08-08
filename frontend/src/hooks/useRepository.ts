import { useQuery } from "@tanstack/react-query";
import { getRepository, getRepositoryFileContent, getRepositoryFiles } from "../services/repos";

export function useRepository(repoId: string | undefined) {
  return useQuery({
    queryKey: ["repo", repoId],
    queryFn: () => getRepository(repoId!),
    enabled: Boolean(repoId),
  });
}

export function useRepositoryFiles(repoId: string | undefined) {
  return useQuery({
    queryKey: ["repo-files", repoId],
    queryFn: () => getRepositoryFiles(repoId!),
    enabled: Boolean(repoId),
  });
}

export function useRepositoryFileContent(repoId: string | undefined, path: string | null) {
  return useQuery({
    queryKey: ["repo-file-content", repoId, path],
    queryFn: () => getRepositoryFileContent(repoId!, path!),
    enabled: Boolean(repoId && path),
  });
}
