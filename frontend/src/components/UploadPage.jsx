import { useState, useEffect, useRef } from "react";
import { api } from "../api/api";
import { FaFileUpload, FaCheckCircle, FaTimesCircle, FaChevronLeft, FaChevronRight } from "react-icons/fa";
import { Toast } from "primereact/toast";

export default function UploadPage() {
  // =================================================================
  // Toast Notification Reference
  // =================================================================
  const toast = useRef(null);

  // =================================================================
  // State Management
  // =================================================================
  const [file, setFile] = useState(null);
  // Removed: message and status states - now using Toast instead
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploads, setUploads] = useState([]);
  const [uploadsLoading, setUploadsLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalUploads, setTotalUploads] = useState(0);
  const pageSize = 10;

  // Load uploads on component mount and when page changes
  useEffect(() => {
    loadUploads();
  }, [currentPage]);

  const loadUploads = async () => {
    try {
      setUploadsLoading(true);
      const response = await api.get("/uploads", {
        params: {
          page: currentPage,
          page_size: pageSize
        }
      });
      setUploads(response.data.uploads || []);
      setTotalPages(response.data.total_pages || 1);
      setTotalUploads(response.data.total_uploads || 0);
    } catch (err) {
      console.error("Failed to load uploads:", err);
    } finally {
      setUploadsLoading(false);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      toast.current.show({
        severity: "error",
        summary: "Error",
        detail: "Please select a file first",
        life: 2000,
      });
      return;
    }

    setLoading(true);
    setUploadProgress(10);
    const formData = new FormData();
    formData.append("file", file);

    try {
      setUploadProgress(50);
      const response = await api.post("/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setUploadProgress(75);
      toast.current.show({
        severity: "success",
        summary: "Success",
        detail: `✅ Upload successful! File ID: ${response.data.upload_id}`,
        life: 2000,
      });
      setFile(null);
      setCurrentPage(1); // Reset to first page
      loadUploads(); // Refresh the list
    } catch (err) {
      toast.current.show({
        severity: "error",
        summary: "Error",
        detail: "❌ Upload failed: " + (err.response?.data?.detail || err.message),
        life: 2000,
      });
    } finally {
      setLoading(false);
      setUploadProgress(0);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-8">
      {/* Toast Notifications */}
      <Toast 
        ref={toast} 
        position="top-center"
        itemTemplate={(item) => (
          <div className="flex items-center gap-3 w-full">
            <div className="flex-shrink-0 text-lg">
              {item.severity === "success" && <FaCheckCircle />}
              {item.severity === "error" && <FaTimesCircle />}
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-bold text-sm">{item.summary}</p>
              <p className="text-sm opacity-95">{item.detail}</p>
            </div>
          </div>
        )}
      />

      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <FaFileUpload className="text-4xl text-blue-600" />
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
            Upload Requirements
          </h1>
        </div>
        <p className="text-gray-600 dark:text-gray-400">
          Upload your requirement document to generate epics, stories, and test plans
        </p>
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Upload Section - Left (takes 2 columns on desktop) */}
        <div className="lg:col-span-2">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 border-2 border-dashed border-blue-300 dark:border-blue-700">
            {/* File Input */}
            <div className="mb-6">
              <label className="block mb-4">
                <div className="flex flex-col items-center justify-center py-12 cursor-pointer hover:bg-blue-50 dark:hover:bg-gray-700 rounded-lg transition-colors">
                  <FaFileUpload className="text-5xl text-blue-500 mb-3" />
                  <p className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                    Click to select file or drag and drop
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Supported formats: PDF, TXT, DOCX
                  </p>
                </div>
                <input
                  type="file"
                  onChange={(e) => {
                    setFile(e.target.files[0]);
                  }}
                  className="hidden"
                  accept=".pdf,.txt,.docx"
                />
              </label>
            </div>

            {/* Selected File Display */}
            {file && (
              <div className="mb-6 p-4 bg-blue-50 dark:bg-blue-900 rounded-lg border border-blue-200 dark:border-blue-700">
                <p className="text-sm text-gray-600 dark:text-gray-400">Selected file:</p>
                <p className="text-lg font-semibold text-blue-600 dark:text-blue-400">
                  📄 {file.name}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Size: {(file.size / 1024).toFixed(2)} KB
                </p>
              </div>
            )}

            {/* Upload Button */}
            <button
              onClick={handleUpload}
              disabled={!file || loading}
              className={`w-full py-3 rounded-lg font-semibold text-white transition-all duration-300 ${
                loading
                  ? "bg-gray-400 cursor-not-allowed"
                  : file
                  ? "bg-blue-600 hover:bg-blue-700 active:scale-95"
                  : "bg-gray-400 cursor-not-allowed"
              }`}
            >
              {loading ? `📤 Uploading... ${uploadProgress}%` : "📤 Upload File"}
            </button>

            {/* Progress Bar */}
            {loading && (
              <div className="mt-4 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
            )}
          </div>

          {/* Info Section */}
          <div className="mt-8 bg-blue-50 dark:bg-blue-900 rounded-lg p-6 border-l-4 border-blue-500">
            <h3 className="text-lg font-bold text-blue-900 dark:text-blue-100 mb-3">
              ℹ️ What happens next?
            </h3>
            <ul className="space-y-2 text-blue-800 dark:text-blue-200 text-sm">
              <li>✅ Your file will be analyzed by AI</li>
              <li>✅ Epics will be automatically generated</li>
              <li>✅ Stories, QA tests, and test plans will be created</li>
              <li>✅ All artifacts will be synced to Confluence</li>
              <li>✅ You can view everything in the respective pages</li>
            </ul>
          </div>
        </div>

        {/* Recent Uploads - Right Section */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            📋 Recent Uploads
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            Total: {totalUploads} files
          </p>

          {/* Loading State */}
          {uploadsLoading && (
            <div className="text-center py-8">
              <p className="text-gray-600 dark:text-gray-400">Loading uploads...</p>
            </div>
          )}

          {/* Uploads List */}
          {!uploadsLoading && uploads.length > 0 && (
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {uploads.map((upload) => (
                <div key={upload.id} className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600">
                  <p className="text-sm font-semibold text-gray-900 dark:text-white truncate">
                    ID: {upload.id}
                  </p>
                  <p className="text-xs text-gray-600 dark:text-gray-400 truncate">
                    {upload.filename}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                    {new Date(upload.created_at).toLocaleDateString()}
                  </p>
                </div>
              ))}
            </div>
          )}

          {/* Empty State */}
          {!uploadsLoading && uploads.length === 0 && (
            <div className="text-center py-8">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                No uploads yet. Upload a file to get started!
              </p>
            </div>
          )}

          {/* Pagination */}
          {!uploadsLoading && uploads.length > 0 && totalPages > 1 && (
            <div className="mt-6 flex items-center justify-between border-t border-gray-200 dark:border-gray-600 pt-4">
              <button
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
                className="p-2 rounded-lg bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition"
                title="Previous page"
              >
                <FaChevronLeft className="text-sm text-gray-700 dark:text-gray-300" />
              </button>

              <span className="text-xs text-gray-600 dark:text-gray-400">
                Page {currentPage} of {totalPages}
              </span>

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
      </div>
    </div>
  );
}
