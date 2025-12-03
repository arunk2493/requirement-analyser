import { NavLink, useNavigate } from "react-router-dom";
import {
  FaHome,
  FaUpload,
  FaBook,
  FaList,
  FaFlask,
  FaCheckSquare,
  FaHistory,
  FaRobot,
  FaSignOutAlt,
  FaUser,
  FaMoon,
  FaSun,
} from "react-icons/fa";
import { clearAuthToken } from "../api/api";

export default function Sidebar({ darkMode, setDarkMode, setIsAuthenticated }) {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("user") || "{}");

  const links = [
    { path: "/", label: "Dashboard", icon: <FaHome /> },
    { path: "/upload", label: "Upload", icon: <FaUpload /> },
    { path: "/agentic-ai", label: "Agentic AI", icon: <FaRobot /> },
    { path: "/epics", label: "Epics", icon: <FaBook /> },
    { path: "/stories", label: "Stories", icon: <FaList /> },
    { path: "/qa", label: "QA", icon: <FaCheckSquare /> },
    { path: "/testplans", label: "Test Plans", icon: <FaFlask /> },
    { path: "/history", label: "History", icon: <FaHistory /> },
  ];

  const handleLogout = () => {
    clearAuthToken();
    setIsAuthenticated(false);
    navigate("/login");
  };

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

      <div className="border-t border-gray-700 pt-4 mt-4 space-y-4">
        {/* User Info */}
        {user.email && (
          <div className="bg-gray-700 dark:bg-gray-800 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-1">
              <FaUser className="text-blue-400 text-sm" />
              <p className="text-xs text-gray-300">Logged in as</p>
            </div>
            <p className="text-sm font-semibold text-white truncate">
              {user.email}
            </p>
          </div>
        )}

        {/* Dark Mode Toggle */}
        <button
          onClick={() => setDarkMode(!darkMode)}
          className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 dark:bg-gray-800 dark:hover:bg-gray-700 text-gray-300 rounded-lg transition-all"
          title={darkMode ? "Light mode" : "Dark mode"}
        >
          {darkMode ? (
            <><FaSun className="text-yellow-400" /> Light</>
          ) : (
            <><FaMoon className="text-blue-400" /> Dark</>
          )}
        </button>

        {/* Logout Button */}
        <button
          onClick={handleLogout}
          className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-all font-semibold"
        >
          <FaSignOutAlt /> Logout
        </button>

        <p className="text-xs text-gray-500 text-center">
          Version 1.0 • AI-Powered Requirements
        </p>
      </div>
    </div>
  );
}
