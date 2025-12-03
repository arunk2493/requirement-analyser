import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import UploadPage from "./components/UploadPage";
import EpicsPage from "./components/EpicsPage";
import StoriesPage from "./components/StoriesPage";
import QAPage from "./components/QAPage";
import TestPlansPage from "./components/TestPlansPage";
import History from "./components/GenerateConfluence";
import AgenticAIPage from "./components/AgenticAIPage";
import Dashboard from "./components/Dashboard";
import LoginPage from "./components/LoginPage";
import { useState, useEffect } from "react";
import { initializeAuthToken } from "./api/api";

// Protected Route wrapper
function ProtectedRoute({ children, isAuthenticated }) {
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

export default function App() {
  const [darkMode, setDarkMode] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Initialize auth token from localStorage and check if user is authenticated
    initializeAuthToken();
    const token = localStorage.getItem("token");
    setIsAuthenticated(!!token);
    setLoading(false);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-100">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className={darkMode ? "dark" : ""}>
      <BrowserRouter>
        {isAuthenticated ? (
          <div className="flex h-screen bg-gray-100 dark:bg-gray-900 transition-colors duration-500">
            <Sidebar
              darkMode={darkMode}
              setDarkMode={setDarkMode}
              setIsAuthenticated={setIsAuthenticated}
            />

            <div className="flex-1 overflow-auto">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/upload" element={<UploadPage />} />
                <Route path="/agentic-ai" element={<AgenticAIPage />} />
                <Route path="/history" element={<History />} />
                <Route path="/epics" element={<EpicsPage />} />
                <Route path="/stories" element={<StoriesPage />} />
                <Route path="/qa" element={<QAPage />} />
                <Route path="/testplans" element={<TestPlansPage />} />
                <Route path="/login" element={<Navigate to="/" replace />} />
              </Routes>
            </div>
          </div>
        ) : (
          <Routes>
            <Route path="/login" element={<LoginPage setIsAuthenticated={setIsAuthenticated} />} />
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        )}
      </BrowserRouter>
    </div>
  );
}
