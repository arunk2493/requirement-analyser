import { useEffect, useState } from "react";
import { fetchAllQA } from "../api/api";
import { FaCheckSquare, FaSpinner, FaSync, FaChevronLeft, FaChevronRight, FaSortUp, FaSortDown, FaCode, FaCopy, FaTimes, FaFilter } from "react-icons/fa";

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
  const [expandedScripts, setExpandedScripts] = useState({});
  const [scriptLanguage, setScriptLanguage] = useState({});
  const [copyNotification, setCopyNotification] = useState(null);
  const [selectedTestTypes, setSelectedTestTypes] = useState([]);
  const [selectedStories, setSelectedStories] = useState([]);
  const [showFilterPanel, setShowFilterPanel] = useState(false);
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

  const generateKarateScript = (test) => {
    const testTitle = test.content?.title || `Test ${test.id}`;
    const testScenarios = test.content?.testScenarios || [];
    
    const scenarios = testScenarios.map((scenario, idx) => 
      `    And match response contains '${scenario.replace(/'/g, "\\'")}'`
    ).join('\n');

    return `Feature: API Automation - ${testTitle}
  
  Background:
    * url 'http://api.example.com'
    * header Accept = 'application/json'

  Scenario: ${testTitle}
    When method get
    Then status 200
${scenarios || '    # Add your test scenarios here'}`;
  };

  const generateJavaScript = (test) => {
    const testTitle = test.content?.title || `Test${test.id}`;
    const className = testTitle.replace(/[^a-zA-Z0-9]/g, '');
    
    return `import io.restassured.RestAssured;
import io.restassured.response.Response;
import org.junit.Test;
import static io.restassured.RestAssured.*;
import static org.hamcrest.Matchers.*;

public class ${className}Test {
  
  @Test
  public void test${className}() {
    RestAssured.baseURI = "http://api.example.com";
    
    Response response = given()
      .header("Accept", "application/json")
      .when()
      .get("/endpoint")
      .then()
      .assertThat()
      .statusCode(200)
      .extract()
      .response();
    
    System.out.println("Response: " + response.asString());
  }
}`;
  };

  const copyToClipboard = (text, qaId) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopyNotification(qaId);
      setTimeout(() => setCopyNotification(null), 2000);
    });
  };

  const toggleScript = (qaId, language) => {
    setExpandedScripts(prev => ({
      ...prev,
      [qaId]: !prev[qaId]
    }));
    setScriptLanguage(prev => ({
      ...prev,
      [qaId]: language
    }));
  };

  const getTestTitle = (qa) => {
    if (typeof qa.content === 'string') {
      try {
        const parsed = JSON.parse(qa.content);
        return parsed.title || parsed.name || 'QA Test';
      } catch {
        return qa.content.substring(0, 50);
      }
    }
    return qa.content?.title || qa.content?.name || 'QA Test';
  };

  const getTestDescription = (qa) => {
    if (typeof qa.content === 'string') {
      return qa.content.substring(0, 100);
    }
    return JSON.stringify(qa.content).substring(0, 100);
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
          View all QA test cases with automation script generation
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
          <div className="flex items-center justify-between mb-4">
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Total QA Tests: <span className="font-bold text-gray-900 dark:text-white">{totalQATests}</span>
            </div>
            <button
              onClick={() => setShowFilterPanel(!showFilterPanel)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition"
              title="Toggle filters"
            >
              <FaFilter />
              Filters
            </button>
          </div>

          {/* Filter Panel */}
          {showFilterPanel && (
            <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 space-y-4">
              
              {/* Filter by Story */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  Filter by Story
                </label>
                <select
                  multiple
                  value={selectedStories}
                  onChange={(e) => {
                    const selected = Array.from(e.target.selectedOptions, option => parseInt(option.value));
                    setSelectedStories(selected);
                    setCurrentPage(1);
                  }}
                  className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {Array.from(new Set(qa.map(test => test.story_id))).map((storyId) => (
                    <option key={storyId} value={storyId}>
                      Story {storyId}
                    </option>
                  ))}
                </select>
                {selectedStories.length > 0 && (
                  <button
                    onClick={() => {
                      setSelectedStories([]);
                      setCurrentPage(1);
                    }}
                    className="mt-2 text-xs text-blue-600 dark:text-blue-400 hover:underline"
                  >
                    Clear story filter
                  </button>
                )}
              </div>

              {/* Filter by Test Type */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  Filter by Test Type
                </label>
                <div className="space-y-2 p-3 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-600">
                  {["functional", "non_functional", "api"].map((testType) => {
                    const testTypeCount = qa.filter(test => (test.test_type || test.content?.type || "functional") === testType).length;
                    const typeColors = {
                      "functional": "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
                      "non_functional": "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
                      "api": "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
                    };
                    const colorClass = typeColors[testType] || "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200";
                    
                    return (
                      <label key={testType} className="flex items-center gap-3 p-2 hover:bg-blue-50 dark:hover:bg-gray-800 rounded cursor-pointer transition">
                        <input
                          type="checkbox"
                          checked={selectedTestTypes.includes(testType)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedTestTypes([...selectedTestTypes, testType]);
                            } else {
                              setSelectedTestTypes(selectedTestTypes.filter(type => type !== testType));
                            }
                            setCurrentPage(1);
                          }}
                          className="w-4 h-4 rounded border-gray-300 dark:border-gray-600 cursor-pointer accent-blue-600"
                        />
                        <span className={`text-xs font-semibold px-2 py-1 rounded ${colorClass}`}>
                          {testType.replace("_", " ").toUpperCase()}
                        </span>
                        <span className="text-xs bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400 px-2 py-1 rounded ml-auto">
                          {testTypeCount}
                        </span>
                      </label>
                    );
                  })}
                </div>
                {selectedTestTypes.length > 0 && (
                  <button
                    onClick={() => {
                      setSelectedTestTypes([]);
                      setCurrentPage(1);
                    }}
                    className="mt-2 text-xs text-blue-600 dark:text-blue-400 hover:underline"
                  >
                    Clear type filter
                  </button>
                )}
              </div>

              {/* Active Filters Summary */}
              {(selectedStories.length > 0 || selectedTestTypes.length > 0) && (
                <div className="p-3 bg-blue-50 dark:bg-blue-900/30 rounded-lg border border-blue-200 dark:border-blue-800">
                  <p className="text-sm text-gray-700 dark:text-gray-300">
                    <span className="font-semibold">Active Filters:</span>
                    {selectedStories.length > 0 && (
                      <span className="ml-2">
                        {selectedStories.length} {selectedStories.length === 1 ? 'story' : 'stories'}
                      </span>
                    )}
                    {selectedStories.length > 0 && selectedTestTypes.length > 0 && (
                      <span className="mx-2">•</span>
                    )}
                    {selectedTestTypes.length > 0 && (
                      <span>
                        {selectedTestTypes.length} {selectedTestTypes.length === 1 ? 'test type' : 'test types'}
                      </span>
                    )}
                  </p>
                </div>
              )}
            </div>
          )}

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
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900 dark:text-white">Test Case Title</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900 dark:text-white">Test Type</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900 dark:text-white">Description</th>
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
                  <th className="px-6 py-3 text-center text-sm font-semibold text-gray-900 dark:text-white">Automation Scripts</th>
                </tr>
              </thead>
              <tbody>
                {qa
                  .filter(test => {
                    if (selectedTestTypes.length === 0) return true;
                    const testType = test.test_type || test.content?.type || "functional";
                    return selectedTestTypes.includes(testType);
                  })
                  .map((test) => (
                    <tr key={test.id} className="border-b border-gray-200 dark:border-gray-700 hover:bg-blue-50 dark:hover:bg-gray-700 transition">
                      <td className="px-6 py-4 text-sm text-gray-900 dark:text-gray-100 font-medium">{test.id}</td>
                      <td className="px-6 py-4 text-sm text-gray-900 dark:text-gray-100 font-semibold">
                        {getTestTitle(test)}
                      </td>
                      <td className="px-6 py-4 text-sm">
                        {(() => {
                          const testType = test.test_type || test.content?.type || "functional";
                          const typeColors = {
                            "functional": "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
                            "non_functional": "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
                            "api": "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
                          };
                          const colorClass = typeColors[testType] || "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200";
                          return (
                            <span className={`px-2 py-1 rounded text-xs font-semibold whitespace-nowrap ${colorClass}`}>
                              {testType.replace("_", " ").toUpperCase()}
                            </span>
                          );
                        })()}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                        {getTestDescription(test)}...
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600 dark:text-gray-400">
                        {new Date(test.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 text-center">
                        <div className="flex items-center justify-center gap-2">
                          <button
                            onClick={() => toggleScript(test.id, 'karate')}
                            className="px-3 py-1 bg-purple-500 hover:bg-purple-600 text-white text-xs rounded transition flex items-center gap-1"
                            title="Generate Karate Script"
                          >
                            <FaCode className="text-xs" />
                            Karate
                          </button>
                          <button
                            onClick={() => toggleScript(test.id, 'java')}
                            className="px-3 py-1 bg-orange-500 hover:bg-orange-600 text-white text-xs rounded transition flex items-center gap-1"
                            title="Generate Java Script"
                          >
                            <FaCode className="text-xs" />
                            Java
                          </button>
                        </div>
                      </td>
                    </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Automation Script Modal */}
          {Object.entries(expandedScripts).map(([qaId, isOpen]) => {
            if (!isOpen) return null;
            const test = qa.find(t => t.id === parseInt(qaId));
            if (!test) return null;
            
            const language = scriptLanguage[qaId];
            const script = language === 'karate' ? generateKarateScript(test) : generateJavaScript(test);
            
            return (
              <div key={qaId} className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-2xl max-w-3xl w-full max-h-96 flex flex-col">
                  {/* Modal Header */}
                  <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
                    <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                      {language === 'karate' ? '🎭 Karate' : '☕ Java'} Automation Script - {getTestTitle(test)}
                    </h3>
                    <button
                      onClick={() => toggleScript(qaId, language)}
                      className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 transition"
                    >
                      <FaTimes className="text-xl" />
                    </button>
                  </div>

                  {/* Modal Body - Script */}
                  <div className="flex-1 overflow-y-auto p-4">
                    <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg font-mono text-xs overflow-x-auto">
                      {script}
                    </pre>
                  </div>

                  {/* Modal Footer */}
                  <div className="flex items-center justify-between p-4 border-t border-gray-200 dark:border-gray-700">
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {copyNotification === parseInt(qaId) && '✓ Copied to clipboard'}
                    </span>
                    <button
                      onClick={() => copyToClipboard(script, parseInt(qaId))}
                      className="flex items-center gap-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded transition"
                    >
                      <FaCopy className="text-sm" />
                      Copy
                    </button>
                  </div>
                </div>
              </div>
            );
          })}

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
