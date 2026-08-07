import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import Sidebar from "./Sidebar";

function renderSidebar(initialPath: string) {
  return render(
    <MemoryRouter initialEntries={[initialPath]}>
      <Routes>
        <Route path="/repo/:repoId/*" element={<Sidebar />} />
        <Route path="*" element={<Sidebar />} />
      </Routes>
    </MemoryRouter>
  );
}

describe("Sidebar", () => {
  it("shows only the dashboard link when no repository is selected", () => {
    renderSidebar("/");
    expect(screen.getByText("Dashboard")).toBeInTheDocument();
    expect(screen.queryByText("Code Review")).not.toBeInTheDocument();
  });

  it("shows repository-scoped links when a repository is selected", () => {
    renderSidebar("/repo/1/review");
    expect(screen.getByText("Dashboard")).toBeInTheDocument();
    expect(screen.getByText("Code Review")).toBeInTheDocument();
    expect(screen.getByText("Health Score")).toBeInTheDocument();
  });

  it("links navigate to the selected repository workspace", () => {
    renderSidebar("/repo/42");
    const reviewLink = screen.getByText("Code Review").closest("a");
    expect(reviewLink).toHaveAttribute("href", "/repo/42/review");
  });
});
