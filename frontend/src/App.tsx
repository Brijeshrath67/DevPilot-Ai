import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import Dashboard from "./pages/Dashboard";
import Repository from "./pages/Repository";
import Review from "./pages/Review";
import Documentation from "./pages/Documentation";
import Testing from "./pages/Testing";
import Chat from "./pages/Chat";
import Health from "./pages/Health";
import Settings from "./pages/Settings";

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/repo/:repoId" element={<Repository />} />
          <Route path="/repo/:repoId/review" element={<Review />} />
          <Route path="/repo/:repoId/docs" element={<Documentation />} />
          <Route path="/repo/:repoId/tests" element={<Testing />} />
          <Route path="/repo/:repoId/chat" element={<Chat />} />
          <Route path="/repo/:repoId/health" element={<Health />} />
          <Route path="/repo/:repoId/settings" element={<Settings />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
