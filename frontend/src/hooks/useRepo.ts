import { useQuery } from "react-query";
import api from "../lib/api";

export function useRepo(repoId: string) {
  return useQuery(
    ["repo", repoId],
    async () => {
      const response = await api.get(`/repos/${repoId}`);
      return response.data;
    },
    {
      enabled: Boolean(repoId),
    }
  );
}
