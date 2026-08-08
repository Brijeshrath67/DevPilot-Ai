import { useQuery } from "@tanstack/react-query";
import { getRepositories } from "../services/repos";

export function useRepositories() {
  return useQuery({ queryKey: ["repositories"], queryFn: getRepositories });
}
