import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AppShell } from "./components/layout/AppShell";
import { ToastProvider } from "./components/ui/Toast";
import { DashboardPage } from "./pages/Dashboard";
import { RepositoryOverviewPage } from "./pages/RepositoryOverview";
import { CodeReviewPage } from "./pages/CodeReview";
import { SecurityPage } from "./pages/Security";
import { DocumentationPage } from "./pages/Documentation";
import { TestingPage } from "./pages/Testing";
import { QAChatPage } from "./pages/QAChat";
import { HealthPage } from "./pages/Health";
import { SettingsPage } from "./pages/Settings";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 15_000,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <ToastProvider>
          <Routes>
            <Route element={<AppShell />}>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/repo/:repoId" element={<RepositoryOverviewPage />} />
              <Route path="/repo/:repoId/review" element={<CodeReviewPage />} />
              <Route path="/repo/:repoId/security" element={<SecurityPage />} />
              <Route path="/repo/:repoId/docs" element={<DocumentationPage />} />
              <Route path="/repo/:repoId/tests" element={<TestingPage />} />
              <Route path="/repo/:repoId/chat" element={<QAChatPage />} />
              <Route path="/repo/:repoId/health" element={<HealthPage />} />
              <Route path="/repo/:repoId/settings" element={<SettingsPage />} />
              <Route path="*" element={<DashboardPage />} />
            </Route>
          </Routes>
        </ToastProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
