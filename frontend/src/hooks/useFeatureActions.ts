import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  analyzeRepository,
  chatWithRepository,
  generateDocumentation,
  generateTests,
  getProjectHealth,
  runCodeReview,
  runSecurityAudit,
} from "../services/repos";

export function useAnalyze(repoId: string | undefined) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (scope: string) => analyzeRepository(repoId!, scope),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["repo", repoId] });
      queryClient.invalidateQueries({ queryKey: ["repo-status", repoId] });
      queryClient.invalidateQueries({ queryKey: ["repo-files", repoId] });
    },
  });
}

export function useCodeReview(repoId: string | undefined) {
  return useMutation({
    mutationFn: (payload: { reviewScope: string; files?: string[] }) =>
      runCodeReview(repoId!, payload.reviewScope, payload.files),
  });
}

export function useSecurityAudit(repoId: string | undefined) {
  return useMutation({
    mutationFn: () => runSecurityAudit(repoId!),
  });
}

export function useDocumentation(repoId: string | undefined) {
  return useMutation({
    mutationFn: (payload: { docTypes: string[]; targetFiles?: string[] }) =>
      generateDocumentation(repoId!, payload.docTypes, payload.targetFiles),
  });
}

export function useTests(repoId: string | undefined) {
  return useMutation({
    mutationFn: (payload: { testTypes: string[]; targetFiles?: string[] }) =>
      generateTests(repoId!, payload.testTypes, payload.targetFiles),
  });
}

export function useChat(repoId: string | undefined) {
  return useMutation({
    mutationFn: (payload: { question: string; sessionId?: string }) =>
      chatWithRepository(repoId!, payload.question, payload.sessionId),
  });
}

export function useProjectHealth(repoId: string | undefined) {
  return useMutation({
    mutationFn: () => getProjectHealth(repoId!),
  });
}
