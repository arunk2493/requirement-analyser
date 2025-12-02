import { useEffect, useState } from "react";
import { fetchAllQA } from "../api/api";
import { FaCheckSquare, FaSpinner, FaSync, FaChevronLeft, FaChevronRight, FaSortUp, FaSortDown } from "react-icons/fa";

export default function QAPage() {
  const [qa, setQA] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalQATests, setTotalQATests] = useState(0);
  const [sortBy, setSortBy] = useState("created_at");
  const [sortOrder, setSortOrder] = useState("desc");
  const pageSize = 10;

  const loadQA = async (page = 1) => {
    try {
      setRefreshing(true);
      const response = await fetchAllQA(page, pageSize, sortBy, sortOrder);
      setQA(response.data.qa_tests || []);
      setTotalQATests(response.data.total_qa_tests || 0);
      setTotalPages(response.data.total_pages || 1);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load QA test cases");
      setQA([]);
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    const initialLoad = async () => {
      try {
        setLoading(true);
        await loadQA(currentPage);
      } finally {
        setLoading(false);
      }
    };
    initialLoad();
  }, [currentPage, sortBy, sortOrder]);

  const toggleExpanded = (qaId) => {
    setExpandedRows(prev => ({
      ...prev,
      [qaId]: !prev[qaId]
    }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <FaCheckSquare className="text-4xl text-blue-600" />
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
              ✅ QA Test Cases
            </h1>
          </div>
          <button
            onClick={() => loadQA()}
            disabled={refreshing}
            className="p-2 bg-blue-500 hover:bg-blue-600 disabled:bg-blue-400 text-white rounded-lg transition"
            title="Refresh QA tests"
          >
            <FaSync className={`text-2xl ${refreshing ? "animate-spin" : ""}`} />
          </button>
        </div>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          View all QA test cases for the selected story
        </p>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-16">
          <FaSpinner className="text-4xl text-blue-500 animate-spin" />
          <p className="ml-4 text-lg text-gray-600 dark:text-gray-400">
            Loading QA test cases...
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
      {!loading && qa.length === 0 && !error && (
        <div className="bg-blue-50 dark:bg-blue-900 rounded-lg p-12 text-center">
          <p className="text-xl text-blue-700 dark:text-blue-100">
            📭 No QA test cases found
          </p>
          <p className="text-blue-600 dark:text-blue-200 mt-2">
            Generate QA test cases to see them here
          </p>
        </div>
      )}

      {/* QA Table */}
      {!loading && qa.length > 0 && (
        <div className="space-y-4">
          <div className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            Total QA Tests: <span className="font-bold text-gray-900 dark:text-white">{totalQATests}</span>
          </div>
          <div className="overflow-x-auto rounded-lg shadow">
            <table className="w-full border-collapse bg-white dark:bg-gray-800">
              <thead>
                <tr className="bg-blue-100 dark:bg-blue-900 border-b border-gray-300 dark:border-gray-700">
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
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900 dark:text-white">Test Case</th>
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
                </tr>
              </thead>
              <tbody>
                {qa.map((test) => (
                    <tr key={test.id} className="border-b border-gray-200 dark:border-gray-700 hover:bg-blue-50 dark:hover:bg-gray-700 transition">
                      <td className="px-6 py-4 text-sm text-gray-900 dark:text-gray-100 font-medium">{test.id}</td>
                      <td className="px-6 py-4 text-sm text-gray-900 dark:text-gray-100 line-clamp-2">{test.content?.substring(0, 50)}...</td>
                      <td className="px-6 py-4 text-sm text-gray-600 dark:text-gray-400">
                        {new Date(test.created_at).toLocaleDateString()}
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
