import { BrowserRouter, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import UploadPage from "./components/UploadPage";
import EpicsPage from "./components/EpicsPage";
import StoriesPage from "./components/StoriesPage";
import QAPage from "./components/QAPage";
import TestPlansPage from "./components/TestPlansPage";
import GenerateConfluence from "./components/GenerateConfluence";
import Dashboard from "./components/Dashboard";
import { useState } from "react";

export default function App() {
  const [darkMode, setDarkMode] = useState(false);

  return (
    <div className={darkMode ? "dark" : ""}>
      <BrowserRouter>
        <div className="flex h-screen bg-gray-100 dark:bg-gray-900 transition-colors duration-500">
          <Sidebar darkMode={darkMode} setDarkMode={setDarkMode} />

          <div className="flex-1 overflow-auto">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/upload" element={<UploadPage />} />
              <Route path="/generate" element={<GenerateConfluence />} />
              <Route path="/epics" element={<EpicsPage />} />
              <Route path="/stories" element={<StoriesPage />} />
              <Route path="/qa" element={<QAPage />} />
              <Route path="/testplans" element={<TestPlansPage />} />
            </Routes>
          </div>
        </div>
      </BrowserRouter>
    </div>
  );
}
