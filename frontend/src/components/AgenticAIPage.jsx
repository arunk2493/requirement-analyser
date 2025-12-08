import { useState, useEffect } from "react";
import { generateEpicsAgent, generateStoriesAgent, generateQAAgent, generateTestPlanAgent, ragSearch, ragVectorStoreSearch, fetchUploads, getEpicsAgent, getStoriesAgent, getQAAgent, getTestPlanAgent } from "../api/api";
import { FaRobot, FaSpinner, FaExternalLinkAlt, FaSync, FaCheckCircle, FaExclamationCircle, FaArrowRight } from "react-icons/fa";

export default function AgenticAIPage() {
  const [uploadId, setUploadId] = useState("");
  const [epicIdForStories, setEpicIdForStories] = useState("");
  const [epicIdForTestPlan, setEpicIdForTestPlan] = useState("");
  const [storyId, setStoryId] = useState("");
  const [ragQuery, setRagQuery] = useState("");

  const [userUploads, setUserUploads] = useState([]);
  const [loadingUploads, setLoadingUploads] = useState(true);
  
  const [loadingEpics, setLoadingEpics] = useState(false);
  const [loadingStories, setLoadingStories] = useState(false);
  const [loadingQA, setLoadingQA] = useState(false);
  const [loadingTestPlan, setLoadingTestPlan] = useState(false);
  const [loadingRAG, setLoadingRAG] = useState(false);

  const [generatedEpics, setGeneratedEpics] = useState([]);
  const [generatedStories, setGeneratedStories] = useState([]);
  const [generatedQA, setGeneratedQA] = useState([]);
  const [generatedTestPlans, setGeneratedTestPlans] = useState([]);
  const [ragResults, setRagResults] = useState([]);

  // Recent items for quick access (last 5)
  const [recentEpics, setRecentEpics] = useState([]);
  const [recentStories, setRecentStories] = useState([]);
  const [recentQA, setRecentQA] = useState([]);

  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  // Fetch user's uploads on component mount and when user logs in
  useEffect(() => {
    const fetchUserUploads = async () => {
      try {
        setLoadingUploads(true);
        const res = await fetchUploads();
        setUserUploads(res.data.uploads || []);
      } catch (error) {
        console.error("Failed to fetch uploads:", error);
        setUserUploads([]);
      } finally {
        setLoadingUploads(false);
      }
    };
    
    // Fetch immediately
    fetchUserUploads();
    
    // Listen for storage changes (user login from another tab/window)
    const handleStorageChange = (e) => {
      if (e.key === 'token' && e.newValue) {
        fetchUserUploads();
      }
    };
    
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  const showMessage = (type, message) => {
    if (type === "success") {
      setSuccessMessage(message);
      setErrorMessage("");
      setTimeout(() => setSuccessMessage(""), 4000);
    } else {
      setErrorMessage(message);
      setSuccessMessage("");
      setTimeout(() => setErrorMessage(""), 4000);
    }
  };

  // Helper function to add item to recent list (keep only last 5, sorted by most recent first)
  const addToRecent = (setRecentFn, item, existingItems = []) => {
    // Create new item with timestamp
    const itemWithTime = { ...item, addedAt: new Date().getTime() };
    
    // Remove duplicates (if item with same id already exists)
    const filtered = existingItems.filter(i => i.id !== item.id);
    
    // Add new item to front and keep only 5 most recent
    const updated = [itemWithTime, ...filtered].slice(0, 5);
    setRecentFn(updated);
  };

  // Generate Epics
  const handleGenerateEpics = async () => {
    if (!uploadId) {
      showMessage("error", "Please select an upload");
      return;
    }
    try {
      setLoadingEpics(true);
      const res = await generateEpicsAgent(parseInt(uploadId));
      const epics = res.data.data?.epics || [];
      setGeneratedEpics(epics);
      showMessage("success", "✅ Epics generated successfully!");
      // Refresh the epics list
      await fetchEpics(uploadId);
    } catch (e) {
      showMessage("error", e.response?.data?.detail?.error || e.response?.data?.detail || "Failed to generate epics");
    } finally {
      setLoadingEpics(false);
    }
  };

  // Fetch epics for selected upload
  const fetchEpics = async (uId) => {
    if (!uId) return;
    try {
      const res = await getEpicsAgent(parseInt(uId));
      const epics = res.data.data?.epics || [];
      setGeneratedEpics(epics);
      // Add each epic to recent list
      epics.forEach(epic => {
        addToRecent(setRecentEpics, epic, recentEpics);
      });
    } catch (error) {
      console.error("Failed to fetch epics:", error);
      const errorMsg = error.response?.data?.detail?.error || error.response?.data?.detail || error.message || "Failed to fetch epics";
      console.error("Detailed error:", errorMsg);
      setGeneratedEpics([]);
    }
  };

  // Handle upload selection
  const handleUploadChange = (e) => {
    const uId = e.target.value;
    setUploadId(uId);
    setGeneratedEpics([]);
    setEpicIdForStories("");
    setEpicIdForTestPlan("");
    setGeneratedStories([]);
    setGeneratedTestPlans([]);
    setStoryId("");
    setGeneratedQA([]);
    // Fetch epics for the selected upload
    if (uId) {
      fetchEpics(uId);
    }
  };

  // Generate Stories
  const handleGenerateStories = async () => {
    if (!epicIdForStories) {
      showMessage("error", "Please select an epic");
      return;
    }
    try {
      setLoadingStories(true);
      const res = await generateStoriesAgent(parseInt(epicIdForStories));
      const stories = res.data.data?.stories || [];
      setGeneratedStories(stories);
      showMessage("success", "✅ Stories generated successfully!");
      // Refresh the stories list
      await fetchStories(epicIdForStories);
    } catch (e) {
      showMessage("error", e.response?.data?.detail?.error || e.response?.data?.detail || "Failed to generate stories");
    } finally {
      setLoadingStories(false);
    }
  };

  // Fetch stories for selected epic
  const fetchStories = async (epicId) => {
    if (!epicId) return;
    console.log("Fetching stories for epic:", epicId);
    try {
      const res = await getStoriesAgent(parseInt(epicId));
      console.log("Stories response:", res.data);
      const stories = res.data.data?.stories || [];
      console.log("Stories to display:", stories);
      setGeneratedStories(stories);
      // Add each story to recent list
      stories.forEach(story => {
        addToRecent(setRecentStories, story, recentStories);
      });
      if (stories.length === 0) {
        console.warn("No stories returned for epic", epicId);
      }
    } catch (error) {
      console.error("Failed to fetch stories:", error);
      const errorMsg = error.response?.data?.detail?.error || error.response?.data?.detail || error.message || "Failed to fetch stories";
      console.error("Detailed error:", errorMsg);
      showMessage("error", `Could not load stories: ${errorMsg}`);
      setGeneratedStories([]);
    }
  };

  // Handle epic selection for stories
  const handleEpicForStoriesChange = (e) => {
    const epicId = e.target.value;
    console.log("Epic selected for stories:", epicId);
    setEpicIdForStories(epicId);
    setGeneratedStories([]);
    setStoryId("");
    setGeneratedQA([]);
    // Fetch stories for the selected epic
    if (epicId) {
      fetchStories(epicId);
    }
  };

  // Generate QA
  const handleGenerateQA = async () => {
    if (!storyId) {
      showMessage("error", "Please select a story");
      return;
    }
    try {
      setLoadingQA(true);
      const res = await generateQAAgent(parseInt(storyId));
      const qa = res.data.data?.qa_tests || res.data.data?.qa || [];
      setGeneratedQA(qa);
      showMessage("success", "✅ QA tests generated successfully!");
      // Refresh the QA list
      await fetchQA(storyId);
    } catch (e) {
      showMessage("error", e.response?.data?.detail?.error || e.response?.data?.detail || "Failed to generate QA tests");
    } finally {
      setLoadingQA(false);
    }
  };

  // Fetch QA for selected story
  const fetchQA = async (sId) => {
    if (!sId) return;
    console.log("Fetching QA for story:", sId);
    try {
      const res = await getQAAgent(parseInt(sId));
      console.log("QA response:", res.data);
      const qa = res.data.data?.qa_tests || res.data.data?.qa || [];
      console.log("QA tests to display:", qa);
      setGeneratedQA(qa);
      // Add each QA to recent list
      qa.forEach(qaItem => {
        addToRecent(setRecentQA, qaItem, recentQA);
      });
      if (qa.length === 0) {
        console.warn("No QA tests returned for story", sId);
      }
    } catch (error) {
      console.error("Failed to fetch QA:", error);
      const errorMsg = error.response?.data?.detail?.error || error.response?.data?.detail || error.message || "Failed to fetch QA";
      console.error("Detailed error:", errorMsg);
      showMessage("error", `Could not load QA tests: ${errorMsg}`);
      setGeneratedQA([]);
    }
  };

  // Handle story selection
  const handleStoryChange = (e) => {
    const sId = e.target.value;
    console.log("Story selected for QA:", sId);
    setStoryId(sId);
    setGeneratedQA([]);
    // Fetch QA for the selected story
    if (sId) {
      fetchQA(sId);
    }
  };

  // Generate Test Plan
  const handleGenerateTestPlan = async () => {
    if (!epicIdForTestPlan) {
      showMessage("error", "Please select an epic");
      return;
    }
    try {
      setLoadingTestPlan(true);
      const res = await generateTestPlanAgent(parseInt(epicIdForTestPlan));
      const testPlans = res.data.data?.test_plans || res.data.test_plans || [];
      setGeneratedTestPlans(testPlans);
      showMessage("success", "✅ Test plan generated successfully!");
      // Refresh the test plans list
      await fetchTestPlans(epicIdForTestPlan);
    } catch (e) {
      showMessage("error", e.response?.data?.detail?.error || e.response?.data?.detail || "Failed to generate test plan");
    } finally {
      setLoadingTestPlan(false);
    }
  };

  // Fetch test plans for selected epic
  const fetchTestPlans = async (epicId) => {
    if (!epicId) return;
    console.log("Fetching test plans for epic:", epicId);
    try {
      const res = await getTestPlanAgent(parseInt(epicId));
      console.log("Test plans response:", res.data);
      const testPlans = res.data.data?.test_plans || [];
      console.log("Test plans to display:", testPlans);
      setGeneratedTestPlans(testPlans);
      if (testPlans.length === 0) {
        console.warn("No test plans returned for epic", epicId);
      }
    } catch (error) {
      console.error("Failed to fetch test plans:", error);
      const errorMsg = error.response?.data?.detail?.error || error.response?.data?.detail || error.message || "Failed to fetch test plans";
      console.error("Detailed error:", errorMsg);
      showMessage("error", `Could not load test plans: ${errorMsg}`);
      setGeneratedTestPlans([]);
    }
  };

  // Handle epic selection for test plan
  const handleEpicForTestPlanChange = (e) => {
    const epicId = e.target.value;
    console.log("Epic selected for test plan:", epicId);
    setEpicIdForTestPlan(epicId);
    setGeneratedTestPlans([]);
    // Fetch test plans for the selected epic
    if (epicId) {
      fetchTestPlans(epicId);
    }
  };

  // RAG Search
  const handleRAGSearch = async () => {
    if (!ragQuery) {
      showMessage("error", "Please enter a search query");
      return;
    }
    try {
      setLoadingRAG(true);
      const res = await ragVectorStoreSearch(ragQuery, 5);
      setRagResults(res.data.search_results || []);
      showMessage("success", `✅ Found ${(res.data.search_results || []).length} documents!`);
    } catch (e) {
      showMessage("error", e.response?.data?.detail || "Failed to search documents");
    } finally {
      setLoadingRAG(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3">
          <FaRobot className="text-4xl text-blue-600" />
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white">🤖 Agentic AI</h1>
        </div>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Use specialized agents to generate epics, stories, and QA tests from your requirements
        </p>
      </div>

      {/* Messages */}
      {successMessage && (
        <div className="mb-6 p-4 bg-green-50 dark:bg-green-900 border-l-4 border-green-500 rounded-lg">
          <p className="text-green-700 dark:text-green-100 flex items-center gap-2">
            <FaCheckCircle /> {successMessage}
          </p>
        </div>
      )}

      {errorMessage && (
        <div className="mb-6 p-4 bg-red-50 dark:bg-red-900 border-l-4 border-red-500 rounded-lg">
          <p className="text-red-700 dark:text-red-100 flex items-center gap-2">
            <FaExclamationCircle /> {errorMessage}
          </p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Generate Epics Card */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold text-purple-600 mb-4">📚 Generate Epics</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Select Upload
              </label>
              {loadingUploads ? (
                <div className="flex items-center justify-center py-2">
                  <FaSpinner className="animate-spin text-purple-500" />
                </div>
              ) : (
                <select
                  value={uploadId}
                  onChange={handleUploadChange}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 outline-none"
                >
                  <option value="">-- Choose an upload --</option>
                  {userUploads.map((upload) => (
                    <option key={upload.id} value={upload.id}>
                      {upload.filename} (ID: {upload.id})
                    </option>
                  ))}
                </select>
              )}
            </div>
            <div className="relative group">
              <button
                onClick={handleGenerateEpics}
                disabled={loadingEpics || !uploadId || generatedEpics.length > 0}
                className="w-full px-4 py-2 bg-purple-500 hover:bg-purple-600 disabled:bg-gray-400 disabled:cursor-not-allowed disabled:opacity-60 text-white font-semibold rounded-lg transition flex items-center justify-center gap-2"
              >
                {loadingEpics ? <FaSpinner className="animate-spin" /> : <FaArrowRight />}
                {loadingEpics ? "Generating..." : "Generate Epics"}
              </button>
              {generatedEpics.length > 0 && (
                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-800 text-white text-sm rounded opacity-0 group-hover:opacity-100 transition whitespace-nowrap pointer-events-none z-10">
                  Epics already present
                </div>
              )}
            </div>
          </div>

          {generatedEpics.length > 0 && (
            <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Generated Epics ({generatedEpics.length})</h3>
              <div className="overflow-x-auto rounded-lg">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-purple-100 dark:bg-purple-900">
                      <th className="px-4 py-2 text-left font-semibold text-gray-900 dark:text-white">ID</th>
                      <th className="px-4 py-2 text-left font-semibold text-gray-900 dark:text-white">Name</th>
                      <th className="px-4 py-2 text-left font-semibold text-gray-900 dark:text-white">Link</th>
                    </tr>
                  </thead>
                  <tbody>
                    {generatedEpics.slice(0, 5).map((epic) => (
                      <tr key={epic.id} className="border-b border-gray-200 dark:border-gray-700 hover:bg-purple-50 dark:hover:bg-gray-700">
                        <td className="px-4 py-2 text-gray-900 dark:text-gray-100">{epic.id}</td>
                        <td className="px-4 py-2 text-gray-900 dark:text-gray-100">{epic.name}</td>
                        <td className="px-4 py-2">
                          {epic.confluence_page_url ? (
                            <a
                              href={epic.confluence_page_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-1 px-2 py-1 bg-purple-500 hover:bg-purple-600 text-white rounded text-xs transition"
                            >
                              <FaExternalLinkAlt /> View
                            </a>
                          ) : (
                            <span className="text-gray-400">N/A</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>

        {/* Generate Test Plan Card */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold text-orange-600 mb-4">📋 Generate Test Plan</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Select Epic
              </label>
              <select
                value={epicIdForTestPlan}
                onChange={handleEpicForTestPlanChange}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-orange-500 outline-none"
              >
                <option value="">-- Choose an epic --</option>
                {generatedEpics.map((epic) => (
                  <option key={epic.id} value={epic.id}>
                    {epic.name} (ID: {epic.id})
                  </option>
                ))}
              </select>
              {generatedEpics.length === 0 && uploadId && (
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                  💡 Generate epics first to create test plans
                </p>
              )}
              {!uploadId && (
                <p className="text-sm text-amber-600 dark:text-amber-400 mt-2">
                  ⚠️ Select an upload from the first card to load epics
                </p>
              )}
            </div>
            <div className="relative group">
              <button
                onClick={handleGenerateTestPlan}
                disabled={loadingTestPlan || !epicIdForTestPlan || generatedTestPlans.length > 0}
                className="w-full px-4 py-2 bg-orange-500 hover:bg-orange-600 disabled:bg-gray-400 disabled:cursor-not-allowed disabled:opacity-60 text-white font-semibold rounded-lg transition flex items-center justify-center gap-2"
              >
                {loadingTestPlan ? <FaSpinner className="animate-spin" /> : <FaArrowRight />}
                {loadingTestPlan ? "Generating..." : "Generate Test Plan"}
              </button>
              {generatedTestPlans.length > 0 && (
                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-800 text-white text-sm rounded opacity-0 group-hover:opacity-100 transition whitespace-nowrap pointer-events-none z-10">
                  Test Plans already present
                </div>
              )}
            </div>
            {generatedTestPlans.length === 0 && epicIdForTestPlan && (
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                💡 No existing test plans found. Generate test plans from the selected epic.
              </p>
            )}
            {!epicIdForTestPlan && generatedEpics.length > 0 && (
              <p className="text-sm text-amber-600 dark:text-amber-400 mt-2">
                ⚠️ Select an epic from the dropdown to load test plans
              </p>
            )}
          </div>

          {generatedTestPlans.length > 0 && (
            <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Generated Test Plans ({generatedTestPlans.length})</h3>
              <div className="overflow-x-auto rounded-lg">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-orange-100 dark:bg-orange-900">
                      <th className="px-4 py-2 text-left font-semibold text-gray-900 dark:text-white">ID</th>
                      <th className="px-4 py-2 text-left font-semibold text-gray-900 dark:text-white">Title</th>
                      <th className="px-4 py-2 text-left font-semibold text-gray-900 dark:text-white">Confluence Link</th>
                    </tr>
                  </thead>
                  <tbody>
                    {generatedTestPlans.map((testPlan) => {
                      let displayName = "Test Plan";
                      try {
                        if (typeof testPlan.content === 'string') {
                          const parsed = JSON.parse(testPlan.content);
                          displayName = parsed.title || parsed.name || "Test Plan";
                        } else if (testPlan.content?.title) {
                          displayName = testPlan.content.title;
                        } else if (testPlan.content?.name) {
                          displayName = testPlan.content.name;
                        }
                      } catch (e) {
                        displayName = testPlan.name || "Test Plan";
                      }
                      
                      return (
                        <tr key={testPlan.id} className="border-b border-gray-200 dark:border-gray-700 hover:bg-orange-50 dark:hover:bg-gray-700">
                          <td className="px-4 py-2 text-gray-900 dark:text-gray-100">{testPlan.id}</td>
                          <td className="px-4 py-2 text-gray-900 dark:text-gray-100">{displayName}</td>
                          <td className="px-4 py-2">
                            {testPlan.confluence_page_url ? (
                              <a
                                href={testPlan.confluence_page_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center gap-1 px-3 py-1 bg-orange-500 hover:bg-orange-600 text-white rounded text-xs transition"
                              >
                                <FaExternalLinkAlt /> View
                              </a>
                            ) : (
                              <span className="text-gray-400">N/A</span>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>

        {/* Generate Stories Card */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold text-green-600 mb-4">📖 Generate Stories</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Select Epic {generatedEpics.length > 0 && <span className="text-green-600">({generatedEpics.length})</span>}
              </label>
              <select
                value={epicIdForStories}
                onChange={handleEpicForStoriesChange}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-green-500 outline-none"
              >
                <option value="">-- Choose an epic --</option>
                {recentEpics.length > 0 && (
                  <optgroup label="📌 Recent Epics">
                    {recentEpics.map((epic) => (
                      <option key={`recent-${epic.id}`} value={epic.id}>
                        ⭐ {epic.name} (ID: {epic.id})
                      </option>
                    ))}
                  </optgroup>
                )}
                {generatedEpics.length > 0 && (
                  <optgroup label="All Epics">
                    {generatedEpics.map((epic) => (
                      <option key={epic.id} value={epic.id}>
                        {epic.name} (ID: {epic.id})
                      </option>
                    ))}
                  </optgroup>
                )}
              </select>
              {generatedEpics.length === 0 && uploadId && (
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                  💡 Select an upload first - epic list will load automatically
                </p>
              )}
              {!uploadId && (
                <p className="text-sm text-amber-600 dark:text-amber-400 mt-2">
                  ⚠️ Select an upload from the first card to load epics
                </p>
              )}
            </div>
            <div className="relative group">
              <button
                onClick={handleGenerateStories}
                disabled={loadingStories || !epicIdForStories || generatedStories.length > 0}
                className="w-full px-4 py-2 bg-green-500 hover:bg-green-600 disabled:bg-gray-400 disabled:cursor-not-allowed disabled:opacity-60 text-white font-semibold rounded-lg transition flex items-center justify-center gap-2"
              >
                {loadingStories ? <FaSpinner className="animate-spin" /> : <FaArrowRight />}
                {loadingStories ? "Generating..." : "Generate Stories"}
              </button>
              {generatedStories.length > 0 && (
                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-800 text-white text-sm rounded opacity-0 group-hover:opacity-100 transition whitespace-nowrap pointer-events-none z-10">
                  Stories already present
                </div>
              )}
            </div>
          </div>

          {generatedStories.length > 0 && (
            <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Generated Stories ({generatedStories.length})</h3>
              <div className="overflow-x-auto rounded-lg">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-green-100 dark:bg-green-900">
                      <th className="px-4 py-2 text-left font-semibold text-gray-900 dark:text-white">ID</th>
                      <th className="px-4 py-2 text-left font-semibold text-gray-900 dark:text-white">Name</th>
                    </tr>
                  </thead>
                  <tbody>
                    {generatedStories.slice(0, 5).map((story) => (
                      <tr key={story.id} className="border-b border-gray-200 dark:border-gray-700 hover:bg-green-50 dark:hover:bg-gray-700">
                        <td className="px-4 py-2 text-gray-900 dark:text-gray-100">{story.id}</td>
                        <td className="px-4 py-2 text-gray-900 dark:text-gray-100">{story.name || "Untitled"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>

        {/* Generate QA Card */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold text-blue-600 mb-4">✅ Generate QA Tests</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Select Story {generatedStories.length > 0 && <span className="text-blue-600">({generatedStories.length})</span>}
              </label>
              <select
                value={storyId}
                onChange={handleStoryChange}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
              >
                <option value="">-- Choose a story --</option>
                {recentStories.length > 0 && (
                  <optgroup label="📌 Recent Stories">
                    {recentStories.map((story) => (
                      <option key={`recent-${story.id}`} value={story.id}>
                        ⭐ {story.name || "Untitled"} (ID: {story.id})
                      </option>
                    ))}
                  </optgroup>
                )}
                {generatedStories.length > 0 && (
                  <optgroup label="All Stories">
                    {generatedStories.map((story) => (
                      <option key={story.id} value={story.id}>
                        {story.name || "Untitled"} (ID: {story.id})
                      </option>
                    ))}
                  </optgroup>
                )}
              </select>
              {generatedStories.length === 0 && epicIdForStories && (
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                  💡 No existing stories found. Generate stories from the selected epic.
                </p>
              )}
              {!epicIdForStories && (
                <p className="text-sm text-amber-600 dark:text-amber-400 mt-2">
                  ⚠️ Select an epic from the Stories card first to load stories
                </p>
              )}
            </div>
            <div className="relative group">
              <button
                onClick={handleGenerateQA}
                disabled={loadingQA || !storyId || generatedQA.length > 0}
                className="w-full px-4 py-2 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed disabled:opacity-60 text-white font-semibold rounded-lg transition flex items-center justify-center gap-2"
              >
                {loadingQA ? <FaSpinner className="animate-spin" /> : <FaArrowRight />}
                {loadingQA ? "Generating..." : "Generate QA Tests"}
              </button>
              {generatedQA.length > 0 && (
                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-800 text-white text-sm rounded opacity-0 group-hover:opacity-100 transition whitespace-nowrap pointer-events-none z-10">
                  QA Tests already present
                </div>
              )}
            </div>
            {generatedQA.length === 0 && storyId && (
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                💡 No existing QA tests found. Generate QA tests from the selected story.
              </p>
            )}
            {!storyId && generatedStories.length > 0 && (
              <p className="text-sm text-amber-600 dark:text-amber-400 mt-2">
                ⚠️ Select a story from the dropdown to load QA tests
              </p>
            )}
          </div>

          {generatedQA.length > 0 && (
            <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Generated QA Tests ({generatedQA.length})</h3>
              <div className="overflow-x-auto rounded-lg">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-blue-100 dark:bg-blue-900">
                      <th className="px-4 py-2 text-left font-semibold text-gray-900 dark:text-white">ID</th>
                      <th className="px-4 py-2 text-left font-semibold text-gray-900 dark:text-white">Title</th>
                    </tr>
                  </thead>
                  <tbody>
                    {generatedQA.slice(0, 5).map((qa) => {
                      // Extract title from content if it's JSON
                      let displayTitle = "QA Test";
                      try {
                        if (typeof qa.content === 'string') {
                          const parsed = JSON.parse(qa.content);
                          displayTitle = parsed.title || parsed.name || "QA Test";
                        } else if (qa.content?.title) {
                          displayTitle = qa.content.title;
                        } else if (qa.content?.name) {
                          displayTitle = qa.content.name;
                        }
                      } catch (e) {
                        displayTitle = String(qa.content).substring(0, 50);
                      }
                      
                      return (
                        <tr key={qa.id} className="border-b border-gray-200 dark:border-gray-700 hover:bg-blue-50 dark:hover:bg-gray-700">
                          <td className="px-4 py-2 text-gray-900 dark:text-gray-100">{qa.id}</td>
                          <td className="px-4 py-2 text-gray-900 dark:text-gray-100">{displayTitle}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>


      </div>
    </div>
  );
}
