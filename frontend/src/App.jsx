import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useState, useEffect } from "react";
import Sidebar from "./components/Sidebar";
import UploadPage from "./components/UploadPage";
import EpicsPage from "./components/EpicsPage";
import StoriesPage from "./components/StoriesPage";
import QAPage from "./components/QAPage";
import TestPlansPage from "./components/TestPlansPage";
import GenerateConfluence from "./components/GenerateConfluence";
import Dashboard from "./components/Dashboard";
import LoginPage from "./components/LoginPage";

function ProtectedRoute({ children, isAuthenticated }) {
  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

export default function App() {
  const [darkMode, setDarkMode] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    setIsAuthenticated(!!token);
    setLoading(false);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-purple-600 to-blue-600">
        <div className="text-center">
          <div className="animate-spin h-12 w-12 border-4 border-white border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-white text-lg font-semibold">Loading...</p>
        </div>
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
                <Route path="/generate" element={<GenerateConfluence />} />
                <Route path="/epics" element={<EpicsPage />} />
                <Route path="/stories" element={<StoriesPage />} />
                <Route path="/qa" element={<QAPage />} />
                <Route path="/testplans" element={<TestPlansPage />} />
                <Route path="/login" element={<Navigate to="/" replace />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </div>
          </div>
        ) : (
          <Routes>
            <Route path="/login" element={<LoginPage setIsAuthenticated={setIsAuthenticated} />} />
            <Route path="/auth/callback" element={<LoginPage setIsAuthenticated={setIsAuthenticated} />} />
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        )}
      </BrowserRouter>
    </div>
  );
}
