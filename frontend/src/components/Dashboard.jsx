import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  FaBook,
  FaList,
  FaCheckSquare,
  FaFlask,
  FaArrowRight,
  FaFileAlt,
} from "react-icons/fa";

export default function Dashboard() {
  const [stats, setStats] = useState({
    uploads: 0,
    epics: 0,
    stories: 0,
    testplans: 0,
  });

  useEffect(() => {
    // Initialize with default values - can be updated with actual API calls
    setStats({
      uploads: 0,
      epics: 0,
      stories: 0,
      testplans: 0,
    });
  }, []);

  const cards = [
    {
      title: "📋 Uploads",
      description: "Manage requirement files",
      icon: <FaFileAlt className="text-4xl" />,
      link: "/upload",
      color: "from-blue-500 to-blue-600",
      count: stats.uploads,
    },
    {
      title: "🎯 Epics",
      description: "View all epics and their details",
      icon: <FaBook className="text-4xl" />,
      link: "/epics",
      color: "from-purple-500 to-purple-600",
      count: stats.epics,
    },
    {
      title: "📖 Stories",
      description: "Browse user stories",
      icon: <FaList className="text-4xl" />,
      link: "/stories",
      color: "from-green-500 to-green-600",
      count: stats.stories,
    },
    {
      title: "✅ Test Plans",
      description: "View test plans and scenarios",
      icon: <FaFlask className="text-4xl" />,
      link: "/testplans",
      color: "from-orange-500 to-orange-600",
      count: stats.testplans,
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-8">
      {/* Header */}
      <div className="mb-12">
        <h1 className="text-5xl font-bold text-gray-900 dark:text-white mb-3">
          🚀 Requirement Analyzer
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-400">
          Manage and organize your requirements, epics, stories, and test plans
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        {cards.map((card, idx) => (
          <Link
            key={idx}
            to={card.link}
            className="group"
          >
            <div
              className={`bg-gradient-to-br ${card.color} rounded-lg shadow-lg p-6 transform transition-all duration-300 hover:shadow-2xl hover:scale-105 cursor-pointer h-full flex flex-col justify-between`}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="text-white opacity-80 group-hover:opacity-100 transition-opacity">
                  {card.icon}
                </div>
                {card.count > 0 && (
                  <span className="bg-white bg-opacity-30 px-3 py-1 rounded-full text-white text-sm font-semibold">
                    {card.count}
                  </span>
                )}
              </div>
              <div>
                <h3 className="text-white font-bold text-lg mb-1">
                  {card.title}
                </h3>
                <p className="text-white text-opacity-90 text-sm">
                  {card.description}
                </p>
              </div>
              <div className="flex items-center mt-4 text-white text-opacity-75 group-hover:text-opacity-100 transition-all">
                <span className="text-sm font-medium">Explore</span>
                <FaArrowRight className="ml-2 transform group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* Info Section */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 mb-8">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          ℹ️ How to Use
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="flex gap-4">
            <div className="text-3xl">📁</div>
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                1. Upload Requirements
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Start by uploading your requirement documents to be analyzed
              </p>
            </div>
          </div>
          <div className="flex gap-4">
            <div className="text-3xl">🎯</div>
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                2. Generate Artifacts
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Generate epics, stories, and test plans from your requirements
              </p>
            </div>
          </div>
          <div className="flex gap-4">
            <div className="text-3xl">🔗</div>
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                3. View & Sync
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                View all artifacts and access Confluence pages directly
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gradient-to-br from-indigo-50 to-blue-50 dark:from-indigo-900 dark:to-blue-900 rounded-lg p-6 border-l-4 border-indigo-500">
          <h3 className="text-lg font-bold text-indigo-900 dark:text-indigo-100 mb-2">
            🧠 AI-Powered Analysis
          </h3>
          <p className="text-indigo-700 dark:text-indigo-200">
            Our AI engine analyzes your requirements and generates comprehensive epics, user stories, and test plans automatically.
          </p>
        </div>
        <div className="bg-gradient-to-br from-emerald-50 to-green-50 dark:from-emerald-900 dark:to-green-900 rounded-lg p-6 border-l-4 border-emerald-500">
          <h3 className="text-lg font-bold text-emerald-900 dark:text-emerald-100 mb-2">
            🔗 Confluence Integration
          </h3>
          <p className="text-emerald-700 dark:text-emerald-200">
            All generated artifacts are automatically synced to Confluence for easy collaboration and documentation.
          </p>
        </div>
      </div>
    </div>
  );
}
