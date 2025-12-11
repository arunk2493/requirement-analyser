import { useState } from "react";
import { ragVectorStoreSearch } from "../api/api";
import { FaSpinner, FaArrowRight, FaTimes } from "react-icons/fa";

export default function SearchDocuments() {
  const [ragQuery, setRagQuery] = useState("");
  const [loadingRAG, setLoadingRAG] = useState(false);
  const [ragResults, setRagResults] = useState([]);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [hasSearched, setHasSearched] = useState(false);

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

  const handleRAGSearch = async () => {
    if (!ragQuery) {
      showMessage("error", "Please enter a search query");
      return;
    }
    try {
      setLoadingRAG(true);
      setHasSearched(true);
      setRagResults([]);
      const res = await ragVectorStoreSearch(ragQuery, 5);
      
      // Filter results by relevance threshold (minimum 45% match)
      let relevantResults = (res.data.search_results || []).filter(
        result => (result.similarity_percentage || 0) >= 45
      );
      
      // Remove acceptanceCriteria from text content
      relevantResults = relevantResults.map(result => ({
        ...result,
        text: result.text ? result.text.replace(/acceptanceCriteria[:\s]*/gi, '').trim() : result.text,
        full_text: result.full_text ? result.full_text.replace(/acceptanceCriteria[:\s]*/gi, '').trim() : result.full_text
      })).filter(result => (result.text && result.text.length > 0) || (result.full_text && result.full_text.length > 0));
      
      setRagResults(relevantResults);
      if (relevantResults.length > 0) {
        showMessage("success", `Found ${relevantResults.length} matching documents`);
      } else {
        showMessage("error", "No matching documents found. Try a different search query.");
      }
    } catch (error) {
      console.error("Error performing RAG search:", error);
      showMessage("error", "Failed to search documents. Please try again.");
    } finally {
      setLoadingRAG(false);
    }
  };

  const handleClear = () => {
    setRagQuery("");
    setRagResults([]);
    setHasSearched(false);
    setErrorMessage("");
    setSuccessMessage("");
  };

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            Search Documents
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Search across all uploaded requirement documents using semantic similarity
          </p>
        </div>

        {/* Messages */}
        {errorMessage && (
          <div className="mb-6 p-4 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-100 rounded-lg border border-red-300 dark:border-red-700">
            {errorMessage}
          </div>
        )}
        {successMessage && (
          <div className="mb-6 p-4 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-100 rounded-lg border border-green-300 dark:border-green-700">
            {successMessage}
          </div>
        )}

        {/* Search Card */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-bold text-orange-600 mb-6">Search by Similarity</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Search Query
              </label>
              <input
                type="text"
                value={ragQuery}
                onChange={(e) => setRagQuery(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleRAGSearch()}
                placeholder="Enter search query (e.g., 'camera requirements', 'design specifications', 'API endpoints')"
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-orange-500 outline-none"
              />
            </div>
            <div className="flex gap-3">
              <button
                onClick={handleRAGSearch}
                disabled={loadingRAG || !ragQuery}
                className="flex-1 px-4 py-3 bg-orange-500 hover:bg-orange-600 disabled:bg-gray-400 disabled:cursor-not-allowed disabled:opacity-60 text-white font-semibold rounded-lg transition flex items-center justify-center gap-2"
              >
                {loadingRAG ? <FaSpinner className="animate-spin" /> : <FaArrowRight />}
                {loadingRAG ? "Searching..." : "Search Documents"}
              </button>
              <button
                onClick={handleClear}
                disabled={loadingRAG}
                className="px-4 py-3 bg-gray-500 hover:bg-gray-600 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition flex items-center justify-center gap-2 min-w-max"
                title="Clear search and results"
              >
                <FaTimes />
                Clear
              </button>
            </div>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              💡 Searches across uploaded documents, Epics, and Test Plans using semantic similarity. Returns top results with minimum 45% relevance threshold.
            </p>
          </div>
        </div>

        {/* Results */}
        {ragResults.length > 0 && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
              Top {ragResults.length} Search Results
            </h2>
            <div className="space-y-4">
              {ragResults.map((doc, idx) => {
                const source = doc.source || "unknown";
                const type = doc.type || "document";
                const documentId = doc.document_id || `doc-${idx}`;
                const similarity = doc.similarity_percentage || 0;
                const text = doc.text || doc.full_text || "No content available";
                const metadata = doc.metadata || {};

                // Determine source badge
                let sourceBadgeColor = "bg-blue-200 dark:bg-blue-700 text-blue-900 dark:text-blue-100";
                let sourceLabel = "Retrieval: Vectorstore";
                if (source === "database") {
                  sourceBadgeColor = "bg-purple-200 dark:bg-purple-700 text-purple-900 dark:text-purple-100";
                  sourceLabel = "Retrieval: Database";
                }

                // Color code based on similarity
                let matchColor = "bg-red-100 dark:bg-red-900 border-red-300 dark:border-red-700";
                if (similarity > 70) matchColor = "bg-green-100 dark:bg-green-900 border-green-300 dark:border-green-700";
                else if (similarity > 50) matchColor = "bg-yellow-100 dark:bg-yellow-900 border-yellow-300 dark:border-yellow-700";

                // Get display name based on type
                let displayName = documentId;
                if (type === "epic" && doc.epic_name) {
                  displayName = `Epic: ${doc.epic_name}`;
                } else if (type === "test_plan" && doc.test_plan_title) {
                  displayName = `Test Plan: ${doc.test_plan_title}`;
                } else if (doc.vectorstore) {
                  displayName = `${doc.vectorstore} / ${documentId}`;
                }

                return (
                  <div key={idx} className={`p-6 rounded-lg border transition hover:shadow-md ${matchColor}`}>
                    <div className="flex items-start justify-between gap-3 mb-3">
                      <div className="flex-1">
                        <p className="text-lg font-bold text-gray-900 dark:text-white">
                          #{idx + 1} - {displayName}
                        </p>
                        <div className="flex items-center gap-2 mt-2 flex-wrap">
                          <span className={`text-xs px-3 py-1 rounded-full font-medium ${sourceBadgeColor}`}>
                            {sourceLabel}
                          </span>
                          <span
                            className={`text-xs font-bold px-3 py-1 rounded-full ${
                              similarity > 70
                                ? "bg-green-500 text-white"
                                : similarity > 50
                                ? "bg-yellow-500 text-white"
                                : "bg-red-500 text-white"
                            }`}
                          >
                            {similarity.toFixed(1)}% match
                          </span>
                        </div>
                      </div>
                    </div>
                    <p className="text-sm text-gray-700 dark:text-gray-300 line-clamp-4 leading-relaxed mb-4">
                      {text.length > 400 ? `${text.substring(0, 400)}...` : text}
                    </p>

                    {/* Metadata Section - Horizontal Layout */}
                    <div className="text-xs border-t border-gray-300 dark:border-gray-600 pt-4 mt-4">
                      <div className="flex flex-wrap gap-4 items-center">
                        {source === "vectorstore" && (
                          <>
                            {metadata.filename && (
                              <div className="flex items-center gap-2">
                                <span className="font-bold text-gray-700 dark:text-gray-300">File:</span>
                                <span className="text-gray-600 dark:text-gray-400 break-words">{metadata.filename}</span>
                              </div>
                            )}
                            {metadata.upload_id && (
                              <div className="flex items-center gap-2">
                                <span className="font-bold text-gray-700 dark:text-gray-300">Upload ID:</span>
                                <span className="text-gray-600 dark:text-gray-400">{metadata.upload_id}</span>
                              </div>
                            )}
                            {metadata.type && (
                              <div className="flex items-center gap-2">
                                <span className="font-bold text-gray-700 dark:text-gray-300">Type:</span>
                                <span className="text-gray-600 dark:text-gray-400">{metadata.type}</span>
                              </div>
                            )}
                          </>
                        )}
                        {source === "database" && type === "epic" && (
                          <>
                            {doc.epic_id && (
                              <div className="flex items-center gap-2">
                                <span className="font-bold text-gray-700 dark:text-gray-300">Epic ID:</span>
                                <span className="text-gray-600 dark:text-gray-400">{doc.epic_id}</span>
                              </div>
                            )}
                            {metadata.upload_id && (
                              <div className="flex items-center gap-2">
                                <span className="font-bold text-gray-700 dark:text-gray-300">Upload ID:</span>
                                <span className="text-gray-600 dark:text-gray-400">{metadata.upload_id}</span>
                              </div>
                            )}
                            <div className="flex items-center gap-2">
                              <span className="font-bold text-gray-700 dark:text-gray-300">Confluence Link:</span>
                              {metadata.confluence_page_id ? (
                                <a
                                  href={metadata.confluence_page_id}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-blue-600 dark:text-blue-400 hover:underline break-words"
                                >
                                  View Page ↗
                                </a>
                              ) : (
                                <span className="text-gray-500 dark:text-gray-400">NA</span>
                              )}
                            </div>
                          </>
                        )}
                        {source === "database" && type === "test_plan" && (
                          <>
                            {doc.test_plan_id && (
                              <div className="flex items-center gap-2">
                                <span className="font-bold text-gray-700 dark:text-gray-300">Test Plan ID:</span>
                                <span className="text-gray-600 dark:text-gray-400">{doc.test_plan_id}</span>
                              </div>
                            )}
                            {doc.epic_id && (
                              <div className="flex items-center gap-2">
                                <span className="font-bold text-gray-700 dark:text-gray-300">Epic ID:</span>
                                <span className="text-gray-600 dark:text-gray-400">{doc.epic_id}</span>
                              </div>
                            )}
                            <div className="flex items-center gap-2">
                              <span className="font-bold text-gray-700 dark:text-gray-300">Confluence Link:</span>
                              {metadata.confluence_page_id ? (
                                <a
                                  href={metadata.confluence_page_id}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-blue-600 dark:text-blue-400 hover:underline break-words"
                                >
                                  View Page ↗
                                </a>
                              ) : (
                                <span className="text-gray-500 dark:text-gray-400">NA</span>
                              )}
                            </div>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loadingRAG && ragResults.length === 0 && hasSearched && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-12 text-center">
            <p className="text-gray-500 dark:text-gray-400 text-lg">
              No results found for "{ragQuery}". Try a different search query.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
