import { useState } from "react";
import axios from "axios";
import { FaRobot, FaSpinner, FaExternalLinkAlt, FaSync, FaCheckCircle, FaExclamationCircle, FaArrowRight } from "react-icons/fa";

const API_BASE = "http://localhost:8000";

export default function AgenticAIPage() {
  const [uploadId, setUploadId] = useState("");
  const [epicId, setEpicId] = useState("");
  const [storyId, setStoryId] = useState("");
  const [ragQuery, setRagQuery] = useState("");

  const [loadingEpics, setLoadingEpics] = useState(false);
  const [loadingStories, setLoadingStories] = useState(false);
  const [loadingQA, setLoadingQA] = useState(false);
  const [loadingRAG, setLoadingRAG] = useState(false);

  const [generatedEpics, setGeneratedEpics] = useState([]);
  const [generatedStories, setGeneratedStories] = useState([]);
  const [generatedQA, setGeneratedQA] = useState([]);
  const [ragResults, setRagResults] = useState([]);

  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

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

  // Generate Epics
  const handleGenerateEpics = async () => {
    if (!uploadId) {
      showMessage("error", "Please enter an Upload ID");
      return;
    }
    try {
      setLoadingEpics(true);
      const res = await axios.post(`${API_BASE}/agents/epic/generate`, {
        upload_id: parseInt(uploadId),
      });
      setGeneratedEpics(res.data.data?.epics || []);
      showMessage("success", "✅ Epics generated successfully!");
    } catch (e) {
      showMessage("error", e.response?.data?.detail || "Failed to generate epics");
    } finally {
      setLoadingEpics(false);
    }
  };

  // Generate Stories
  const handleGenerateStories = async () => {
    if (!epicId) {
      showMessage("error", "Please enter an Epic ID");
      return;
    }
    try {
      setLoadingStories(true);
      const res = await axios.post(`${API_BASE}/agents/story/generate`, {
        epic_id: parseInt(epicId),
      });
      setGeneratedStories(res.data.data?.stories || []);
      showMessage("success", "✅ Stories generated successfully!");
    } catch (e) {
      showMessage("error", e.response?.data?.detail || "Failed to generate stories");
    } finally {
      setLoadingStories(false);
    }
  };

  // Generate QA
  const handleGenerateQA = async () => {
    if (!storyId) {
      showMessage("error", "Please enter a Story ID");
      return;
    }
    try {
      setLoadingQA(true);
      const res = await axios.post(`${API_BASE}/agents/qa/generate`, {
        story_id: parseInt(storyId),
      });
      setGeneratedQA(res.data.data?.qa_tests || []);
      showMessage("success", "✅ QA tests generated successfully!");
    } catch (e) {
      showMessage("error", e.response?.data?.detail || "Failed to generate QA tests");
    } finally {
      setLoadingQA(false);
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
      const res = await axios.post(`${API_BASE}/agents/rag/search`, {
        query: ragQuery,
        upload_id: uploadId ? parseInt(uploadId) : null,
        top_k: 5,
      });
      setRagResults(res.data.data?.documents || []);
      showMessage("success", "✅ Documents retrieved successfully!");
    } catch (e) {
      showMessage("error", e.response?.data?.detail || "Failed to retrieve documents");
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
                Upload ID
              </label>
              <input
                type="number"
                value={uploadId}
                onChange={(e) => setUploadId(e.target.value)}
                placeholder="Enter upload ID"
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 outline-none"
              />
            </div>
            <button
              onClick={handleGenerateEpics}
              disabled={loadingEpics || !uploadId}
              className="w-full px-4 py-2 bg-purple-500 hover:bg-purple-600 disabled:bg-purple-400 text-white font-semibold rounded-lg transition flex items-center justify-center gap-2"
            >
              {loadingEpics ? <FaSpinner className="animate-spin" /> : <FaArrowRight />}
              {loadingEpics ? "Generating..." : "Generate Epics"}
            </button>
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

        {/* Generate Stories Card */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold text-green-600 mb-4">📖 Generate Stories</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Epic ID
              </label>
              <input
                type="number"
                value={epicId}
                onChange={(e) => setEpicId(e.target.value)}
                placeholder="Enter epic ID"
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-green-500 outline-none"
              />
            </div>
            <button
              onClick={handleGenerateStories}
              disabled={loadingStories || !epicId}
              className="w-full px-4 py-2 bg-green-500 hover:bg-green-600 disabled:bg-green-400 text-white font-semibold rounded-lg transition flex items-center justify-center gap-2"
            >
              {loadingStories ? <FaSpinner className="animate-spin" /> : <FaArrowRight />}
              {loadingStories ? "Generating..." : "Generate Stories"}
            </button>
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
                Story ID
              </label>
              <input
                type="number"
                value={storyId}
                onChange={(e) => setStoryId(e.target.value)}
                placeholder="Enter story ID"
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
              />
            </div>
            <button
              onClick={handleGenerateQA}
              disabled={loadingQA || !storyId}
              className="w-full px-4 py-2 bg-blue-500 hover:bg-blue-600 disabled:bg-blue-400 text-white font-semibold rounded-lg transition flex items-center justify-center gap-2"
            >
              {loadingQA ? <FaSpinner className="animate-spin" /> : <FaArrowRight />}
              {loadingQA ? "Generating..." : "Generate QA Tests"}
            </button>
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
                    {generatedQA.slice(0, 5).map((qa) => (
                      <tr key={qa.id} className="border-b border-gray-200 dark:border-gray-700 hover:bg-blue-50 dark:hover:bg-gray-700">
                        <td className="px-4 py-2 text-gray-900 dark:text-gray-100">{qa.id}</td>
                        <td className="px-4 py-2 text-gray-900 dark:text-gray-100">{qa.title || "Untitled"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>

        {/* RAG Search Card */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold text-orange-600 mb-4">🔍 RAG Search</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Search Query
              </label>
              <input
                type="text"
                value={ragQuery}
                onChange={(e) => setRagQuery(e.target.value)}
                placeholder="Enter search query"
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-orange-500 outline-none"
              />
            </div>
            <button
              onClick={handleRAGSearch}
              disabled={loadingRAG || !ragQuery}
              className="w-full px-4 py-2 bg-orange-500 hover:bg-orange-600 disabled:bg-orange-400 text-white font-semibold rounded-lg transition flex items-center justify-center gap-2"
            >
              {loadingRAG ? <FaSpinner className="animate-spin" /> : <FaArrowRight />}
              {loadingRAG ? "Searching..." : "Search Documents"}
            </button>
          </div>

          {ragResults.length > 0 && (
            <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Retrieved Documents ({ragResults.length})</h3>
              <div className="space-y-3">
                {ragResults.slice(0, 3).map((doc, idx) => (
                  <div key={idx} className="p-3 bg-orange-50 dark:bg-orange-900 rounded-lg border border-orange-200 dark:border-orange-700">
                    <p className="text-xs font-semibold text-orange-600 dark:text-orange-300 mb-1">Document {idx + 1}</p>
                    <p className="text-sm text-gray-700 dark:text-gray-300 line-clamp-2">{doc.text || doc.content || "No content"}</p>
                    <p className="text-xs text-gray-600 dark:text-gray-400 mt-2">
                      Similarity: {(doc.similarity || 0).toFixed(3)}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
