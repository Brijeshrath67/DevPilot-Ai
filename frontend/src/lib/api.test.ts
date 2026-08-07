import { describe, it, expect } from "vitest";
import api from "./api";

describe("api client", () => {
  it("targets the Vite-injected API base URL", () => {
    const expected = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";
    expect(api.defaults.baseURL).toBe(expected);
  });

  it("uses JSON content-type by default", () => {
    expect(api.defaults.headers["Content-Type"]).toBe("application/json");
  });
});
