import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { Sidebar } from "./Sidebar";

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
  it("shows all items with scoped links disabled when no repository is selected", () => {
    renderSidebar("/");
    expect(screen.getByText("Dashboard")).toBeInTheDocument();
    const reviewLink = screen.getByText("Code Review").closest("a");
    expect(reviewLink).toBeInTheDocument();
    expect(reviewLink).toHaveAttribute("aria-disabled", "true");
    expect(reviewLink).toHaveAttribute("href", "/");
  });

  it("shows repository-scoped links when a repository is selected", () => {
    renderSidebar("/repo/1/review");
    expect(screen.getByText("Dashboard")).toBeInTheDocument();
    expect(screen.getByText("Code Review")).toBeInTheDocument();
    expect(screen.getByText("Security")).toBeInTheDocument();
    expect(screen.getByText("Documentation")).toBeInTheDocument();
    expect(screen.getByText("Tests")).toBeInTheDocument();
    expect(screen.getByText("QA Chat")).toBeInTheDocument();
    expect(screen.getByText("Health")).toBeInTheDocument();
  });

  it("links navigate to the selected repository workspace", () => {
    renderSidebar("/repo/42");
    const reviewLink = screen.getByText("Code Review").closest("a");
    expect(reviewLink).toHaveAttribute("href", "/repo/42/review");
    const securityLink = screen.getByText("Security").closest("a");
    expect(securityLink).toHaveAttribute("href", "/repo/42/security");
  });
});
