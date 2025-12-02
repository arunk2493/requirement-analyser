import { NavLink } from "react-router-dom";
import {
  FaHome,
  FaUpload,
  FaBook,
  FaList,
  FaFlask,
  FaCheckSquare,
  FaFileAlt,
} from "react-icons/fa";

export default function Sidebar({ darkMode, setDarkMode }) {
  const links = [
    { path: "/", label: "Dashboard", icon: <FaHome /> },
    { path: "/upload", label: "Upload", icon: <FaUpload /> },
      { path: "/generate", label: "Generate Confluence", icon: <FaFileAlt /> },
    { path: "/epics", label: "Epics", icon: <FaBook /> },
    { path: "/stories", label: "Stories", icon: <FaList /> },
    { path: "/qa", label: "QA", icon: <FaCheckSquare /> },
    { path: "/testplans", label: "Test Plans", icon: <FaFlask /> },
  ];

  return (
    <div className="w-72 bg-gradient-to-b from-gray-800 to-gray-900 dark:from-gray-900 dark:to-black p-6 flex flex-col shadow-2xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white flex items-center gap-2">
          <span className="text-4xl">🚀</span> Analyzer
        </h1>
        <p className="text-gray-400 text-sm mt-1">Requirement Analysis Tool</p>
      </div>

      <nav className="flex-1 space-y-1">
        {links.map((link) => (
          <NavLink
            key={link.path}
            to={link.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-300 ${
                isActive
                  ? "bg-gradient-to-r from-blue-600 to-blue-500 text-white shadow-lg"
                  : "text-gray-300 hover:bg-gray-700 dark:hover:bg-gray-800"
              }`
            }
          >
            <span className="text-lg">{link.icon}</span>
            <span className="font-medium">{link.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-gray-700 pt-4 mt-4">
        <p className="text-xs text-gray-500 text-center">
          Version 1.0 • AI-Powered Requirements
        </p>
      </div>
    </div>
  );
}
