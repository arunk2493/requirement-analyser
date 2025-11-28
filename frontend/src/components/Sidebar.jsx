import { NavLink } from "react-router-dom";
//import ThemeToggle from "./ThemeToggle";

export default function Sidebar() {
  const links = [
    { path: "/", label: "Dashboard" },
    { path: "/upload", label: "Upload" },
    { path: "/epics", label: "Epics" },
    { path: "/stories", label: "Stories" },
    { path: "/qa", label: "QA" },
  ];

  return (
    <div className="w-60 bg-gray-100 dark:bg-gray-900 p-4 flex flex-col">
      <h1 className="text-2xl font-bold mb-6 text-gray-900 dark:text-gray-100">Analyzer</h1>
      <nav className="flex-1 space-y-2">
        {links.map((link) => (
          <NavLink
            key={link.path}
            to={link.path}
            className={({ isActive }) =>
              `block px-4 py-2 rounded ${
                isActive ? "bg-blue-500 text-white" : "text-gray-800 dark:text-gray-200 hover:bg-gray-300 dark:hover:bg-gray-700"
              }`
            }
          >
            {link.label}
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
