import { useEffect, useState } from "react";
import { fetchAllTestPlans } from "../api/api";
import { FaFlask, FaSpinner, FaExternalLinkAlt, FaSync, FaChevronLeft, FaChevronRight, FaSortUp, FaSortDown } from "react-icons/fa";

export default function TestPlansPage() {
  const [testplans, setTestPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalTestPlans, setTotalTestPlans] = useState(0);
  const [sortBy, setSortBy] = useState("created_at");
  const [sortOrder, setSortOrder] = useState("desc");
  const pageSize = 10;

  const loadTestPlans = async (page = 1) => {
    try {
      setRefreshing(true);
      const response = await fetchAllTestPlans(page, pageSize, sortBy, sortOrder);
      setTestPlans(response.data.test_plans || []);
      setTotalTestPlans(response.data.total_test_plans || 0);
      setTotalPages(response.data.total_pages || 1);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load test plans");
      setTestPlans([]);
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    const initialLoad = async () => {
      try {
        setLoading(true);
        await loadTestPlans(currentPage);
      } finally {
        setLoading(false);
      }
    };
    initialLoad();
  }, [currentPage, sortBy, sortOrder]);

  const toggleExpanded = (planId) => {
    setExpandedRows(prev => ({
      ...prev,
      [planId]: !prev[planId]
    }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <FaFlask className="text-4xl text-orange-600" />
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
              Test Plans
            </h1>
          </div>
          <button
            onClick={() => loadTestPlans()}
            disabled={refreshing}
            className="p-2 bg-orange-500 hover:bg-orange-600 disabled:bg-orange-400 text-white rounded-lg transition"
            title="Refresh test plans"
          >
            <FaSync className={`text-2xl ${refreshing ? "animate-spin" : ""}`} />
          </button>
        </div>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          View all test plans for the selected epic with Confluence links
        </p>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-16">
          <FaSpinner className="text-4xl text-orange-500 animate-spin" />
          <p className="ml-4 text-lg text-gray-600 dark:text-gray-400">
            Loading test plans...
          </p>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900 border-l-4 border-red-500 p-4 rounded-lg mb-6">
          <p className="text-red-700 dark:text-red-100">
            <span className="font-bold">❌ Error:</span> {error}
          </p>
        </div>
      )}

      {/* Empty State */}
      {!loading && testplans.length === 0 && !error && (
        <div className="bg-orange-50 dark:bg-orange-900 rounded-lg p-12 text-center">
          <p className="text-xl text-orange-700 dark:text-orange-100">
            📭 No test plans found
          </p>
          <p className="text-orange-600 dark:text-orange-200 mt-2">
            Generate test plans to see them here
          </p>
        </div>
      )}

      {/* Test Plans Table */}
      {!loading && testplans.length > 0 && (
        <div className="space-y-4">
          <div className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            Total Test Plans: <span className="font-bold text-gray-900 dark:text-white">{totalTestPlans}</span>
          </div>
          <div className="overflow-x-auto rounded-lg shadow">
            <table className="w-full border-collapse bg-white dark:bg-gray-800">
              <thead>
                <tr className="bg-orange-100 dark:bg-orange-900 border-b border-gray-300 dark:border-gray-700">
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900 dark:text-white">
                    <button className="flex items-center gap-2" onClick={() => {
                      if (sortBy === 'id') {
                        setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc');
                      } else {
                        setSortBy('id');
                        setSortOrder('desc');
                      }
                      setCurrentPage(1);
                    }}>
                      ID
                      {sortBy === 'id' ? (sortOrder === 'asc' ? <FaSortUp /> : <FaSortDown />) : null}
                    </button>
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900 dark:text-white">Title</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900 dark:text-white">
                    <button className="flex items-center gap-2" onClick={() => {
                      if (sortBy === 'created_at') {
                        setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc');
                      } else {
                        setSortBy('created_at');
                        setSortOrder('desc');
                      }
                      setCurrentPage(1);
                    }}>
                      Created
                      {sortBy === 'created_at' ? (sortOrder === 'asc' ? <FaSortUp /> : <FaSortDown />) : null}
                    </button>
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900 dark:text-white">Confluence</th>
                </tr>
              </thead>
              <tbody>
                {testplans.map((plan) => (
                    <tr key={plan.id} className="border-b border-gray-200 dark:border-gray-700 hover:bg-orange-50 dark:hover:bg-gray-700 transition">
                      <td className="px-6 py-4 text-sm text-gray-900 dark:text-gray-100 font-medium">{plan.id}</td>
                      <td className="px-6 py-4 text-sm text-gray-900 dark:text-gray-100">{plan.title || (plan.content?.title ?? (typeof plan.content === 'string' ? plan.content.substring(0,50) : JSON.stringify(plan.content).substring(0,50)))}</td>
                      <td className="px-6 py-4 text-sm text-gray-600 dark:text-gray-400">
                        {new Date(plan.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 text-sm">
                        {plan.confluence_page_url ? (
                          <a
                            href={plan.confluence_page_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-2 px-3 py-1 bg-orange-500 hover:bg-orange-600 text-white rounded-md transition"
                          >
                            <FaExternalLinkAlt className="text-xs" />
                            <span>View</span>
                          </a>
                        ) : (
                          <span className="text-gray-400 dark:text-gray-500">N/A</span>
                        )}
                      </td>
                    </tr>
                ))}
              </tbody>
            </table>
          </div>
          {/* Pagination */}
          {totalPages > 1 && (
            <div className="mt-4 flex items-center justify-between">
              <button
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
                className="p-2 rounded-lg bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition"
                title="Previous page"
              >
                <FaChevronLeft className="text-sm text-gray-700 dark:text-gray-300" />
              </button>

              <span className="text-xs text-gray-600 dark:text-gray-400">Page {currentPage} of {totalPages}</span>

              <button
                onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                disabled={currentPage === totalPages}
                className="p-2 rounded-lg bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition"
                title="Next page"
              >
                <FaChevronRight className="text-sm text-gray-700 dark:text-gray-300" />
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
