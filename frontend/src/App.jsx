import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useState, useEffect } from "react";
import Sidebar from "./components/Sidebar";
import LoginPage from "./components/LoginPage";
import UploadPage from "./components/UploadPage";
import EpicsPage from "./components/EpicsPage";
import StoriesPage from "./components/StoriesPage";
import QAPage from "./components/QAPage";
import TestPlansPage from "./components/TestPlansPage";
import History from "./components/GenerateConfluence";
import AgenticAIPage from "./components/AgenticAIPage";
import Dashboard from "./components/Dashboard";
import SearchDocuments from "./components/SearchDocuments";
import JiraIntegration from "./components/JiraIntegration";

export default function App() {
  const [darkMode, setDarkMode] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check if user is logged in on app load
  useEffect(() => {
    try {
      const token = localStorage.getItem("token");
      const email = localStorage.getItem("email");
      
      if (token && email) {
        setIsAuthenticated(true);
        setUser({ email });
      }
    } catch (error) {
      console.error("Error checking authentication:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-100">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // If not authenticated, show login page
  if (!isAuthenticated) {
    return <LoginPage setIsAuthenticated={setIsAuthenticated} setUser={setUser} />;
  }

  // If authenticated, show app with routes
  return (
    <BrowserRouter>
      <div className={darkMode ? "dark" : ""}>
        <div className="flex h-screen bg-gray-100 dark:bg-gray-900 transition-colors duration-500">
          <Sidebar 
            darkMode={darkMode} 
            setDarkMode={setDarkMode}
            user={user}
            setIsAuthenticated={setIsAuthenticated}
            setUser={setUser}
          />

          <div className="flex-1 overflow-auto">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/upload" element={<UploadPage />} />
              <Route path="/agentic-ai" element={<AgenticAIPage />} />
              <Route path="/search-documents" element={<SearchDocuments />} />
              <Route path="/history" element={<History />} />
              <Route path="/epics" element={<EpicsPage />} />
              <Route path="/stories" element={<StoriesPage />} />
              <Route path="/qa" element={<QAPage />} />
              <Route path="/testplans" element={<TestPlansPage />} />
              <Route path="/jira-integration" element={<JiraIntegration />} />
              <Route path="*" element={<Navigate to="/" />} />
            </Routes>
          </div>
        </div>
      </div>
    </BrowserRouter>
  );
}
