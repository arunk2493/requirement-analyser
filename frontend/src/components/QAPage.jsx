import { useEffect, useState } from "react";
import { fetchAllQA } from "../api/api";
import { FaCheckSquare, FaSpinner, FaCode, FaCopy, FaTimes, FaDownload } from "react-icons/fa";
import { Button } from "primereact/button";
import { DataTable } from "primereact/datatable";
import { Column } from "primereact/column";
import { InputText } from "primereact/inputtext";
import { Paginator } from "primereact/paginator";
import { Dropdown } from "primereact/dropdown";
import { Checkbox } from "primereact/checkbox";

export default function QAPage() {
  const [qa, setQA] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const [first, setFirst] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [totalQATests, setTotalQATests] = useState(0);
  const [expandedScripts, setExpandedScripts] = useState({});
  const [scriptLanguage, setScriptLanguage] = useState({});
  const [copyNotification, setCopyNotification] = useState(null);
  const [selectedTestTypes, setSelectedTestTypes] = useState([]);
  const [selectedStories, setSelectedStories] = useState([]);
  const [showFilterPanel, setShowFilterPanel] = useState(false);
  const [allQA, setAllQA] = useState([]);
  const [originalTotalCount, setOriginalTotalCount] = useState(0);
  const [globalFilter, setGlobalFilter] = useState("");

  const loadQA = async () => {
    try {
      setRefreshing(true);
      
      // Fetch all data by getting all pages (in case there are more than 100 tests)
      let allTests = [];
      let currentFetchPage = 1;
      let hasMoreData = true;
      
      while (hasMoreData) {
        const response = await fetchAllQA(currentFetchPage, 100);
        const pageTests = response.data.qa_tests || [];
        allTests = [...allTests, ...pageTests];
        
        // Store original total count from first response
        if (currentFetchPage === 1) {
          setOriginalTotalCount(response.data.total_qa_tests || allTests.length);
        }
        
        // Check if we've fetched all data
        if (allTests.length >= response.data.total_qa_tests || pageTests.length === 0) {
          hasMoreData = false;
        }
        
        currentFetchPage++;
      }
      
      setAllQA(allTests);
      
      // Apply filters if any are active
      const filteredTests = allTests.filter(test => {
        // Filter by story ID
        if (selectedStories.length > 0 && !selectedStories.includes(test.story_id)) {
          return false;
        }
        // Filter by test type
        if (selectedTestTypes.length > 0) {
          const testType = test.test_type || test.content?.type || "functional";
          if (!selectedTestTypes.includes(testType)) {
            return false;
          }
        }
        return true;
      });

      // Calculate total filtered items
      const filteredTotal = filteredTests.length;
      
      // Get paginated results based on first offset
      const page = Math.floor(first / pageSize) + 1;
      const startIdx = (page - 1) * pageSize;
      const endIdx = startIdx + pageSize;
      const paginatedTests = filteredTests.slice(startIdx, endIdx);

      setQA(paginatedTests);
      setTotalQATests(filteredTotal);
      setError(null);
    } catch (err) {
      let errorMessage = "Failed to load QA test cases";
      
      if (err.response?.data?.detail) {
        errorMessage = typeof err.response.data.detail === 'string' 
          ? err.response.data.detail 
          : JSON.stringify(err.response.data.detail);
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
      setQA([]);
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    const initialLoad = async () => {
      try {
        setLoading(true);
        await loadQA();
      } finally {
        setLoading(false);
      }
    };
    initialLoad();
  }, [first, pageSize, selectedStories, selectedTestTypes]);

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

  const testTypeBodyTemplate = (rowData) => {
    const testType = rowData.test_type || rowData.content?.type || "functional";
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
  };

  const descriptionBodyTemplate = (rowData) => {
    return getTestDescription(rowData) + "...";
  };

  const createdAtBodyTemplate = (rowData) => {
    return new Date(rowData.created_at).toLocaleDateString();
  };

  const automationScriptsBodyTemplate = (rowData) => {
    return (
      <div className="flex items-center justify-center gap-2">
        <button
          onClick={() => toggleScript(rowData.id, 'karate')}
          className="px-3 py-1 bg-purple-500 hover:bg-purple-600 text-white text-xs rounded transition flex items-center gap-1"
          title="Generate Karate Script"
        >
          <FaCode className="text-xs" />
          Karate
        </button>
        <button
          onClick={() => toggleScript(rowData.id, 'java')}
          className="px-3 py-1 bg-orange-500 hover:bg-orange-600 text-white text-xs rounded transition flex items-center gap-1"
          title="Generate Java Script"
        >
          <FaCode className="text-xs" />
          Java
        </button>
      </div>
    );
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

  const downloadAsCSV = () => {
    // Get data to download - either filtered or all
    const dataToDownload = allQA.filter(test => {
      // Apply same filters as display
      if (selectedStories.length > 0 && !selectedStories.includes(test.story_id)) {
        return false;
      }
      if (selectedTestTypes.length > 0) {
        const testType = test.test_type || test.content?.type || "functional";
        if (!selectedTestTypes.includes(testType)) {
          return false;
        }
      }
      return true;
    });

    // Prepare CSV content
    const headers = ["ID", "Title", "Type", "Description"];
    const rows = dataToDownload.map(test => [
      test.id,
      `"${getTestTitle(test).replace(/"/g, '""')}"`, // Escape quotes in CSV
      test.test_type || test.content?.type || "functional",
      `"${getTestDescription(test).replace(/"/g, '""')}"` // Escape quotes in CSV
    ]);

    // Combine headers and rows
    const csvContent = [
      headers.join(","),
      ...rows.map(row => row.join(","))
    ].join("\n");

    // Create blob and download
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    
    // Create datetime timestamp in format: YYYY-MM-DD_HH-mm-ss
    const now = new Date();
    const dateTimeStamp = now.toISOString().replace('T', '_').replace(/[:.]/g, '-').slice(0, 19);
    const fileName = `qa_test_cases_${dateTimeStamp}.csv`;
    
    link.setAttribute("href", url);
    link.setAttribute("download", fileName);
    link.style.visibility = "hidden";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <FaCheckSquare className="text-4xl text-blue-600" />
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
              QA Test Cases
            </h1>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={downloadAsCSV}
              disabled={qa.length === 0}
              className="p-2 bg-green-500 hover:bg-green-600 disabled:bg-green-400 text-white rounded-lg transition flex items-center gap-2"
              title="Download as CSV"
            >
              <FaDownload className="text-xl" />
              <span className="text-sm font-medium">Download CSV</span>
            </button>
            <Button
              icon="pi pi-refresh"
              label="Refresh"
              onClick={() => loadQA()}
              disabled={refreshing}
              className="p-button-rounded p-button-text"
              style={{ color: '#3b82f6' }}
              title="Refresh QA tests"
              loading={refreshing}
            />
          </div>
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
            <span className="font-bold">❌ Error:</span> {typeof error === 'string' ? error : JSON.stringify(error)}
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
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {selectedStories.length > 0 || selectedTestTypes.length > 0 ? (
                <>
                  Filtered QA Tests: <span className="font-bold text-gray-900 dark:text-white">{totalQATests}</span>
                  <span className="mx-2">/</span>
                  Total: <span className="font-bold text-gray-900 dark:text-white">{originalTotalCount}</span>
                </>
              ) : (
                <>
                  Total QA Tests: <span className="font-bold text-gray-900 dark:text-white">{totalQATests}</span>
                </>
              )}
            </span>
            <div className="flex items-center gap-2">
              <span className="p-input-icon-left">
                <i className="pi pi-search" />
                <InputText
                  value={globalFilter}
                  onChange={(e) => setGlobalFilter(e.target.value)}
                  placeholder="Search test cases..."
                  className="w-full md:w-auto"
                />
              </span>
              <Button
                icon="pi pi-filter"
                label={showFilterPanel ? "Hide Filters" : "Show Filters"}
                onClick={() => setShowFilterPanel(!showFilterPanel)}
                className="p-button-outlined"
                style={{ borderColor: '#3b82f6', color: '#3b82f6' }}
              />
            </div>
          </div>

          {/* Filter Panel */}
          {showFilterPanel && (
            <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 space-y-4">
              
              {/* Filter by Story */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                  Filter by Story (Jira ID)
                </label>
                <div className="space-y-2 p-3 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-600 max-h-48 overflow-y-auto">
                  {Array.from(new Set(allQA.map(test => test.story_id))).sort().map((storyId) => {
                    const storyTest = allQA.find(test => test.story_id === storyId);
                    const jiraKey = storyTest?.story_jira_key || `Story ${storyId}`;
                    const storyName = storyTest?.story_name || `Story ${storyId}`;
                    const storyTestCount = allQA.filter(test => test.story_id === storyId).length;
                    
                    return (
                      <div key={storyId} className="flex items-center gap-3 p-2 hover:bg-blue-50 dark:hover:bg-gray-800 rounded transition">
                        <Checkbox
                          checked={selectedStories.includes(storyId)}
                          onChange={(e) => {
                            if (e.checked) {
                              setSelectedStories([...selectedStories, storyId]);
                            } else {
                              setSelectedStories(selectedStories.filter(id => id !== storyId));
                            }
                            setFirst(0);
                          }}
                        />
                        <div className="flex-1">
                          <span className="text-sm font-semibold text-gray-900 dark:text-white">
                            {jiraKey}
                          </span>
                          <span className="text-xs text-gray-500 dark:text-gray-400 block">
                            {storyName}
                          </span>
                        </div>
                        <span className="text-xs bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400 px-2 py-1 rounded">
                          {storyTestCount}
                        </span>
                      </div>
                    );
                  })}
                </div>
                {selectedStories.length > 0 && (
                  <Button
                    label={`Clear story filter (${selectedStories.length} selected)`}
                    onClick={() => {
                      setSelectedStories([]);
                      setFirst(0);
                    }}
                    className="p-button-text p-button-sm mt-2"
                    style={{ color: '#3b82f6' }}
                  />
                )}
              </div>

              {/* Filter by Test Type */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                  Filter by Test Type
                </label>
                <div className="space-y-2 p-3 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-600">
                  {["functional", "non_functional", "api"].map((testType) => {
                    // Count tests of this type (accounting for story filter, using all data)
                    const testTypeCount = allQA.filter(test => {
                      if (selectedStories.length > 0 && !selectedStories.includes(test.story_id)) {
                        return false;
                      }
                      const testTypeVal = test.test_type || test.content?.type || "functional";
                      return testTypeVal === testType;
                    }).length;
                    
                    const typeColors = {
                      "functional": "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
                      "non_functional": "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
                      "api": "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
                    };
                    const colorClass = typeColors[testType] || "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200";
                    
                    return (
                      <div key={testType} className="flex items-center gap-3 p-2 hover:bg-blue-50 dark:hover:bg-gray-800 rounded transition">
                        <Checkbox
                          checked={selectedTestTypes.includes(testType)}
                          onChange={(e) => {
                            if (e.checked) {
                              setSelectedTestTypes([...selectedTestTypes, testType]);
                            } else {
                              setSelectedTestTypes(selectedTestTypes.filter(type => type !== testType));
                            }
                            setFirst(0);
                          }}
                        />
                        <span className={`text-xs font-semibold px-2 py-1 rounded ${colorClass}`}>
                          {testType.replace("_", " ").toUpperCase()}
                        </span>
                        <span className="text-xs bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400 px-2 py-1 rounded ml-auto">
                          {testTypeCount}
                        </span>
                      </div>
                    );
                  })}
                </div>
                {selectedTestTypes.length > 0 && (
                  <Button
                    label="Clear type filter"
                    onClick={() => {
                      setSelectedTestTypes([]);
                      setFirst(0);
                    }}
                    className="p-button-text p-button-sm mt-2"
                    style={{ color: '#3b82f6' }}
                  />
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
                  {(() => {
                    const filteredCount = allQA.filter(test => {
                      if (selectedStories.length > 0 && !selectedStories.includes(test.story_id)) {
                        return false;
                      }
                      if (selectedTestTypes.length > 0) {
                        const testType = test.test_type || test.content?.type || "functional";
                        if (!selectedTestTypes.includes(testType)) {
                          return false;
                        }
                      }
                      return true;
                    }).length;
                    return (
                      <p className="text-xs text-gray-600 dark:text-gray-400 mt-2">
                        Showing <span className="font-semibold">{totalQATests}</span> test(s) out of {originalTotalCount}
                      </p>
                    );
                  })()}
                </div>
              )}
            </div>
          )}

          <div className="overflow-x-auto rounded-lg shadow">
            <DataTable
              value={qa}
              globalFilter={globalFilter}
              emptyMessage="No QA test cases found"
              className="p-datatable-striped p-datatable-sm"
              responsiveLayout="scroll"
              stripedRows
              loading={refreshing}
              dataKey="id"
              scrollable
              scrollHeight="600px"
              style={{ borderRadius: '0.5rem' }}
            >
              <Column
                field="id"
                header="ID"
                sortable
                style={{ width: '80px' }}
                bodyClassName="text-gray-900 dark:text-gray-100 font-medium"
              />
              <Column
                field="title"
                header="Test Case Title"
                style={{ width: '300px' }}
                body={(rowData) => getTestTitle(rowData)}
                bodyClassName="text-gray-900 dark:text-gray-100"
              />
              <Column
                header="Test Type"
                style={{ width: '150px' }}
                body={testTypeBodyTemplate}
              />
              <Column
                header="Description"
                style={{ width: '250px' }}
                body={descriptionBodyTemplate}
                bodyClassName="text-gray-600 dark:text-gray-400 line-clamp-2"
              />
              <Column
                field="created_at"
                header="Created"
                sortable
                style={{ width: '150px' }}
                body={createdAtBodyTemplate}
                bodyClassName="text-gray-600 dark:text-gray-400"
              />
              <Column
                header="Automation Scripts"
                style={{ width: '200px' }}
                body={automationScriptsBodyTemplate}
              />
            </DataTable>
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
          {totalQATests > 0 && (
            <div className="mt-6 flex items-center justify-center gap-4">
              <Paginator
                first={first}
                rows={pageSize}
                totalRecords={totalQATests}
                onPageChange={(e) => {
                  setFirst(e.first);
                }}
                template="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink"
              />
              <Dropdown
                value={pageSize}
                onChange={(e) => {
                  setPageSize(e.value);
                  setFirst(0);
                }}
                options={[5, 10, 20, 50]}
                className="p-dropdown-compact"
                style={{ width: '70px' }}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
