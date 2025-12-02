import { useState } from "react";
import {
  FaChevronDown,
  FaChevronUp,
  FaExternalLinkAlt,
  FaCalendar,
  FaTag,
} from "react-icons/fa";

export default function TestPlanCard({ testplan }) {
  const [expanded, setExpanded] = useState(false);

  const renderContent = (obj, level = 0) => {
    if (!obj) return null;

    if (typeof obj === "string" || typeof obj === "number" || typeof obj === "boolean") {
      return (
        <p className={`text-gray-700 dark:text-gray-300 ${level > 0 ? "ml-4" : ""}`}>
          {String(obj)}
        </p>
      );
    }

    if (Array.isArray(obj)) {
      return (
        <ul className="list-disc list-inside space-y-2">
          {obj.map((item, idx) => (
            <li key={idx} className="text-gray-700 dark:text-gray-300">
              {typeof item === "string" ? item : JSON.stringify(item)}
            </li>
          ))}
        </ul>
      );
    }

    if (typeof obj === "object") {
      return (
        <div className="space-y-3">
          {Object.entries(obj).map(([key, value]) => (
            <div key={key} className={level > 0 ? "ml-4" : ""}>
              <p className="font-semibold text-gray-900 dark:text-gray-100 capitalize">
                {key.replace(/([A-Z])/g, " $1").trim()}:
              </p>
              <div className="mt-1">
                {renderContent(value, level + 1)}
              </div>
            </div>
          ))}
        </div>
      );
    }

    return <p className="text-gray-700 dark:text-gray-300">{JSON.stringify(obj)}</p>;
  };

  const getTestPlanTitle = () => {
    if (testplan.content?.title) return testplan.content.title;
    if (testplan.content?.name) return testplan.content.name;
    return "Test Plan";
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-all duration-300 border-l-4 border-orange-500">
      {/* Header */}
      <div
        onClick={() => setExpanded(!expanded)}
        className="p-6 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
      >
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <span className="text-2xl">📋</span>
              <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                {getTestPlanTitle()}
              </h3>
            </div>
            <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
              <div className="flex items-center gap-1">
                <FaTag className="text-orange-500" />
                <span>ID: {testplan.id}</span>
              </div>
              {testplan.created_at && (
                <div className="flex items-center gap-1">
                  <FaCalendar className="text-orange-500" />
                  <span>{new Date(testplan.created_at).toLocaleDateString()}</span>
                </div>
              )}
            </div>
          </div>
          <button
            className="text-orange-600 dark:text-orange-400 hover:text-orange-700 dark:hover:text-orange-300 p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-all"
            onClick={(e) => {
              e.stopPropagation();
              setExpanded(!expanded);
            }}
          >
            {expanded ? (
              <FaChevronUp className="text-xl" />
            ) : (
              <FaChevronDown className="text-xl" />
            )}
          </button>
        </div>
      </div>

      {/* Confluence Link */}
      {testplan.confluence_page_url && (
        <div className="px-6 py-3 bg-gradient-to-r from-orange-50 to-amber-50 dark:from-orange-900 dark:to-amber-900 border-t border-orange-200 dark:border-orange-700">
          <a
            href={testplan.confluence_page_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-orange-600 dark:text-orange-400 hover:text-orange-700 dark:hover:text-orange-300 font-medium text-sm transition-colors"
          >
            <FaExternalLinkAlt />
            <span>View in Confluence</span>
          </a>
        </div>
      )}

      {/* Content */}
      {expanded && (
        <div className="px-6 py-6 bg-gray-50 dark:bg-gray-700 border-t border-gray-200 dark:border-gray-600">
          <div className="space-y-4">
            <div>
              <h4 className="font-bold text-gray-900 dark:text-white mb-3 text-lg">
                📊 Test Plan Details
              </h4>
              <div className="bg-white dark:bg-gray-800 rounded-lg p-4 space-y-3">
                {renderContent(testplan.content)}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
