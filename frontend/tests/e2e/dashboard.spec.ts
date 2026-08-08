import { test, expect, Page } from "@playwright/test";
import { existsSync, mkdirSync } from "node:fs";
import * as path from "node:path";
import { fileURLToPath } from "node:url";
import { execSync } from "node:child_process";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "..", "..", "..");
const SAMPLE_REPO = path.join(REPO_ROOT, "examples", "sample_repo");
const TMP_DIR = path.join(REPO_ROOT, "frontend", "test-results", "fixtures");
const SAMPLE_ZIP = path.join(TMP_DIR, "sample_repo.zip");

function buildSampleZip() {
  if (existsSync(SAMPLE_ZIP)) return;
  mkdirSync(TMP_DIR, { recursive: true });
  execSync(
    `python "${path.join(REPO_ROOT, "scripts", "make_sample_zip.py")}" "${SAMPLE_REPO}" "${SAMPLE_ZIP}"`
  );
}

async function ingestSampleRepository(page: Page): Promise<string> {
  buildSampleZip();
  await page.goto("/");

  // Open the import modal, switch to ZIP upload, name the workspace and submit.
  await page.getByRole("button", { name: "New workspace" }).first().click();
  await page.getByRole("tab", { name: "ZIP upload" }).click();
  await page.getByPlaceholder("Auto-derived from the archive").fill("E2E Sample Repo");
  await page.setInputFiles('input[type="file"]', SAMPLE_ZIP);
  await page.getByRole("button", { name: "Create workspace" }).click();

  // The overview page opens after the archive is stored.
  await page.waitForURL(/\/repo\/\d+/, { timeout: 60_000 });

  // Run the analysis to index files and generate the project summary.
  await page.getByRole("button", { name: "Run analysis", exact: true }).click();
  await expect(page.getByText("Project summary")).toBeVisible({ timeout: 60_000 });

  const match = page.url().match(/\/repo\/(\d+)/);
  expect(match).not.toBeNull();
  return match![1];
}

test.describe("DevPilot AI end-to-end", () => {
  test("ingests a repository and runs the full analysis workflow", async ({ page }) => {
    const repoId = await ingestSampleRepository(page);

    await expect(page.locator("h1", { hasText: "E2E Sample Repo" })).toBeVisible();
    await expect(page.getByText("calculator.py").first()).toBeVisible();
    expect(parseInt(repoId, 10)).toBeGreaterThan(0);
  });

  test("runs a code review and displays severity findings", async ({ page }) => {
    await ingestSampleRepository(page);

    await page.getByText("Code Review").first().click();
    await page.getByRole("button", { name: "Run code review" }).click();

    await expect(page.getByRole("heading", { name: "Findings summary" })).toBeVisible({ timeout: 30_000 });
    await expect(page.getByText(/CRITICAL|HIGH|MEDIUM/).first()).toBeVisible();
    await expect(page.getByText("Recommendations").first()).toBeVisible();
  });

  test("computes and displays project health scores", async ({ page }) => {
    await ingestSampleRepository(page);

    await page.getByText("Health").first().click();
    await page.getByRole("button", { name: "Check health" }).first().click();

    await expect(page.getByText("Score breakdown")).toBeVisible({ timeout: 30_000 });
    await expect(page.getByText(/Good|Fair|Needs attention/).first()).toBeVisible();
  });

  test("runs a security scan and surfaces remediation items", async ({ page }) => {
    await ingestSampleRepository(page);

    await page.getByText("Security").first().click();
    await page.getByRole("button", { name: "Run security audit" }).click();

    await expect(page.getByText("Findings summary")).toBeVisible({ timeout: 30_000 });
    await expect(page.getByText(/CRITICAL|HIGH|MEDIUM/).first()).toBeVisible();
    await expect(page.getByText("Recommendations").first()).toBeVisible();
  });
});
