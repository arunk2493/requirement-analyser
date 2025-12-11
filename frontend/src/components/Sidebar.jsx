import { NavLink } from "react-router-dom";
import { useState } from "react";
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
  FaUserCircle,
  FaSearch,
  FaChevronLeft,
  FaChevronRight,
  FaJira,
} from "react-icons/fa";

export default function Sidebar({ darkMode, setDarkMode, user, setIsAuthenticated, setUser }) {
  const [isCollapsed, setIsCollapsed] = useState(true);

  const links = [
    { path: "/", label: "Dashboard", icon: <FaHome /> },
    { path: "/upload", label: "Upload", icon: <FaUpload /> },
    { path: "/agentic-ai", label: "Agentic AI", icon: <FaRobot /> },
    { path: "/epics", label: "Epics", icon: <FaBook /> },
    { path: "/stories", label: "Stories", icon: <FaList /> },
    { path: "/qa", label: "QA", icon: <FaCheckSquare /> },
    { path: "/testplans", label: "Test Plans", icon: <FaFlask /> },
    { path: "/search-documents", label: "Search Documents", icon: <FaSearch /> },
    { path: "/jira-integration", label: "Jira Integration", icon: <FaJira /> },
    { path: "/history", label: "History", icon: <FaHistory /> },
  ];

  const handleLogout = () => {
    // Clear authentication data
    localStorage.removeItem("token");
    localStorage.removeItem("email");
    
    // Clear all user selections and preferences
    localStorage.removeItem("lastSelectedUploadId");
    localStorage.removeItem("lastSelectedEpicForStories");
    localStorage.removeItem("lastSelectedStoryId");
    localStorage.removeItem("lastSelectedEpicForTestPlan");
    localStorage.removeItem("jira_credentials");
    
    // Reset state
    setIsAuthenticated(false);
    setUser(null);
    
    // Page will auto-refresh due to state change in App.jsx
  };

  return (
    <div className={`transition-all duration-300 bg-gradient-to-b from-gray-800 to-gray-900 dark:from-gray-900 dark:to-black flex flex-col shadow-2xl ${
      isCollapsed ? "w-20" : "w-72"
    }`}>
      {/* Header with Collapse Button */}
      <div className={`p-6 flex items-center justify-between border-b border-gray-700`}>
        <NavLink
          to="/"
          className="relative group"
          title="Requirement Analyzer - Go to Dashboard"
        >
          <div className="text-4xl cursor-pointer hover:scale-110 transition-transform duration-200">
            🚀
          </div>
          {isCollapsed && (
            <div className="absolute left-full ml-3 top-1/2 -translate-y-1/2 bg-gray-900 dark:bg-gray-700 text-white px-3 py-2 rounded-lg text-sm font-medium whitespace-nowrap pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity duration-200 z-50">
              Requirement Analyzer
            </div>
          )}
        </NavLink>
        {!isCollapsed && (
          <div>
            <h1 className="text-3xl font-bold text-white flex items-center gap-2">
              <span className="text-4xl">🚀</span> Analyzer
            </h1>
            <p className="text-gray-400 text-sm mt-1">Requirement Analysis Tool</p>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-2 px-3 py-6">
        {links.map((link) => (
          <div key={link.path} className="relative group">
            <NavLink
              to={link.path}
              className={({ isActive }) =>
                `flex items-center gap-4 px-4 py-3 rounded-lg transition-all duration-300 ${
                  isActive
                    ? "bg-gradient-to-r from-blue-600 to-blue-500 text-white shadow-lg"
                    : "text-gray-300 hover:bg-gray-700 dark:hover:bg-gray-800"
                } ${isCollapsed ? "justify-center" : ""}`
              }
              title={isCollapsed ? link.label : ""}
            >
              <span className="text-lg flex-shrink-0">{link.icon}</span>
              {!isCollapsed && <span className="font-medium text-sm">{link.label}</span>}
            </NavLink>
            
            {/* Tooltip for collapsed state */}
            {isCollapsed && (
              <div className="absolute left-full ml-3 top-1/2 -translate-y-1/2 bg-gray-900 dark:bg-gray-700 text-white px-3 py-2 rounded-lg text-sm font-medium whitespace-nowrap pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity duration-200 z-50">
                {link.label}
              </div>
            )}
          </div>
        ))}
      </nav>

      {/* User Profile Section */}
      <div className={`border-t border-gray-700 py-4 px-3 space-y-3 flex flex-col h-full`}>
        {user && (
          <div className="relative group">
            <div className={`flex items-center gap-3 bg-gray-700 dark:bg-gray-800 rounded-lg p-3 transition-all ${
              isCollapsed ? "justify-center" : "justify-start"
            }`}>
              <FaUserCircle className="text-blue-400 flex-shrink-0 text-xl" />
              {!isCollapsed && (
                <div className="flex-1 min-w-0">
                  <p className="text-xs text-gray-300 font-medium">Logged in as</p>
                  <p className="text-sm font-bold text-white truncate">{user.email}</p>
                </div>
              )}
            </div>
            
            {/* Tooltip for user info when collapsed */}
            {isCollapsed && (
              <div className="absolute left-full ml-3 top-1/2 -translate-y-1/2 bg-gray-900 dark:bg-gray-700 text-white px-3 py-2 rounded-lg text-sm font-bold whitespace-nowrap pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity duration-200 z-50">
                {user.email}
              </div>
            )}
          </div>
        )}
        
        <div className="relative group mt-auto pt-2">
          <button
            onClick={handleLogout}
            className={`w-full flex items-center gap-3 bg-red-600 hover:bg-red-700 text-white font-medium py-3 rounded-lg transition-colors ${
              isCollapsed ? "justify-center px-0" : "justify-start px-4"
            }`}
            title={isCollapsed ? "Logout" : ""}
          >
            <FaSignOutAlt className="flex-shrink-0 text-lg" />
            {!isCollapsed && <span className="text-sm">Logout</span>}
          </button>
          
          {/* Tooltip for logout button when collapsed */}
          {isCollapsed && (
            <div className="absolute left-full ml-3 top-1/2 -translate-y-1/2 bg-gray-900 dark:bg-gray-700 text-white px-3 py-2 rounded-lg text-sm font-medium whitespace-nowrap pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity duration-200 z-50">
              Logout
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
