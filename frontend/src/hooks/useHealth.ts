import { useQuery } from "react-query";
import api from "../lib/api";

export function useHealth(repoId: string) {
  return useQuery(
    ["repoHealth", repoId],
    async () => {
      const response = await api.get(`/repos/${repoId}/health`);
      return response.data;
    },
    {
      enabled: Boolean(repoId),
    }
  );
}
