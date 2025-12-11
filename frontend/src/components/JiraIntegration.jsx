import { useState, useEffect } from "react";
import { FaJira, FaSave, FaTrash, FaExclamationTriangle, FaCheck } from "react-icons/fa";

const API_BASE_URL = "http://localhost:8000";

export default function JiraIntegration() {
  const [formData, setFormData] = useState({
    jira_url: "",
    jira_username: "",
    jira_api_token: "",
    jira_project_key: "",
  });

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState(null);

  const token = localStorage.getItem("token");

  useEffect(() => {
    // Load credentials from backend on component mount
    const loadCredentials = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/jira/get-credentials`, {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        });

        const data = await response.json();

        if (response.ok && data.credentials) {
          setFormData(data.credentials);
          setConnectionStatus("success");
        } else {
          // No credentials saved, try localStorage for backwards compatibility
          const savedCredentials = localStorage.getItem("jira_credentials");
          if (savedCredentials) {
            const parsed = JSON.parse(savedCredentials);
            setFormData(parsed);
            if (parsed.jira_url && parsed.jira_username && parsed.jira_api_token && parsed.jira_project_key) {
              setConnectionStatus("success");
            }
          }
        }
      } catch (err) {
        console.error("Failed to load credentials:", err);
        // Fallback to localStorage
        const savedCredentials = localStorage.getItem("jira_credentials");
        if (savedCredentials) {
          const parsed = JSON.parse(savedCredentials);
          setFormData(parsed);
          if (parsed.jira_url && parsed.jira_username && parsed.jira_api_token && parsed.jira_project_key) {
            setConnectionStatus("success");
          }
        }
      }
    };

    if (token) {
      loadCredentials();
    }
  }, [token]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
    setMessage("");
    setError("");
  };

  const validateForm = () => {
    if (!formData.jira_url.trim()) {
      setError("Jira URL is required");
      return false;
    }
    if (!formData.jira_url.startsWith("http://") && !formData.jira_url.startsWith("https://")) {
      setError("Jira URL must start with http:// or https://");
      return false;
    }
    if (!formData.jira_username.trim()) {
      setError("Jira username/email is required");
      return false;
    }
    if (!formData.jira_api_token.trim()) {
      setError("Jira API token is required");
      return false;
    }
    if (!formData.jira_project_key.trim()) {
      setError("Jira project key is required");
      return false;
    }
    return true;
  };

  const handleTestConnection = async () => {
    if (!validateForm()) {
      return;
    }

    try {
      setLoading(true);
      setMessage("");
      setError("");
      setConnectionStatus(null);

      const response = await fetch(`${API_BASE_URL}/api/jira/test-connection`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok) {
        // Save credentials to backend
        const saveResponse = await fetch(`${API_BASE_URL}/api/jira/save-credentials`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify(formData),
        });

        if (saveResponse.ok) {
          setConnectionStatus("success");
          setMessage(`Connected as ${data.user}. Credentials saved!`);
          // Also save to localStorage for offline use
          localStorage.setItem("jira_credentials", JSON.stringify(formData));
        } else {
          setConnectionStatus("warning");
          setMessage(`Connected as ${data.user}. But failed to save to profile.`);
        }
      } else {
        setConnectionStatus("error");
        setError(data.detail || "Failed to connect to Jira");
      }
    } catch (err) {
      setConnectionStatus("error");
      setError(`Error testing connection: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleClearCredentials = async () => {
    try {
      setLoading(true);
      // Delete from backend
      await fetch(`${API_BASE_URL}/api/jira/delete-credentials`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });
    } catch (err) {
      console.error("Error deleting credentials from backend:", err);
    }

    // Clear localStorage
    localStorage.removeItem("jira_credentials");
    setFormData({
      jira_url: "",
      jira_username: "",
      jira_api_token: "",
      jira_project_key: "",
    });
    setConnectionStatus(null);
    setMessage("");
    setError("");
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 mb-6">
          <div className="flex items-center gap-4 mb-4">
            <FaJira className="text-4xl text-blue-600" />
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
              Jira Integration
            </h1>
          </div>
          <p className="text-gray-600 dark:text-gray-400">
            Connect to Jira using your API token to create epics and stories.
            Your credentials are saved to your account and persist across sessions.
          </p>
        </div>

        {/* Status Messages */}
        {message && (
          <div className="mb-6 p-4 bg-green-100 dark:bg-green-900 border border-green-400 dark:border-green-700 text-green-800 dark:text-green-200 rounded-lg flex items-start gap-3">
            <FaCheck className="text-xl mt-0.5 flex-shrink-0" />
            <span>{message}</span>
          </div>
        )}

        {error && (
          <div className="mb-6 p-4 bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-700 text-red-800 dark:text-red-200 rounded-lg flex items-start gap-3">
            <FaExclamationTriangle className="text-xl mt-0.5 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Main Content */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
          {/* Configuration Section */}
          <div className="p-8">
              {connectionStatus === "success" && (
                <div className="mb-6 p-4 bg-green-50 dark:bg-green-900 border border-green-200 dark:border-green-700 rounded-lg flex items-center justify-between">
                  <p className="text-green-900 dark:text-green-200">
                    <strong>Connected:</strong> {formData.jira_url} ({formData.jira_project_key})
                  </p>
                  <button
                    onClick={handleClearCredentials}
                    className="text-sm px-3 py-1 bg-green-600 hover:bg-green-700 text-white rounded"
                  >
                    Clear
                  </button>
                </div>
              )}

              <div className="space-y-6">
                {/* Jira URL */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Jira URL <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="url"
                    name="jira_url"
                    value={formData.jira_url}
                    onChange={handleInputChange}
                    placeholder="https://your-domain.atlassian.net"
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Your Jira Cloud or Server URL
                  </p>
                </div>

                {/* Jira Username/Email */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Jira Email/Username <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="email"
                    name="jira_username"
                    value={formData.jira_username}
                    onChange={handleInputChange}
                    placeholder="your-email@example.com"
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Your Jira account email or username
                  </p>
                </div>

                {/* Jira API Token */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Jira API Token <span className="text-red-500">*</span>
                  </label>
                  <div className="relative">
                    <input
                      type={showPassword ? "text" : "password"}
                      name="jira_api_token"
                      value={formData.jira_api_token}
                      onChange={handleInputChange}
                      placeholder="Your API token"
                      className="w-full px-4 py-2 pr-12 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                    >
                      {showPassword ? "Hide" : "Show"}
                    </button>
                  </div>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Generate at: Account Settings → Security → API tokens
                  </p>
                </div>

                {/* Jira Project Key */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Project Key <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    name="jira_project_key"
                    value={formData.jira_project_key}
                    onChange={handleInputChange}
                    placeholder="PROJ"
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent uppercase"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    The key of your Jira project (e.g., PROJ, TEST)
                  </p>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-4 pt-4">
                  <button
                    onClick={handleTestConnection}
                    disabled={loading}
                    className="flex items-center gap-2 px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium rounded-lg transition-colors"
                  >
                    {connectionStatus === "success" ? <FaCheck /> : <FaSave />}
                    {loading ? "Testing..." : "Test Connection"}
                  </button>
                </div>
              </div>
            </div>
        </div>

        {/* Help Section */}
        <div className="mt-8 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
            How to Get Your Jira API Token
          </h2>
          <ol className="space-y-4 text-gray-700 dark:text-gray-400">
            <li className="flex gap-4">
              <span className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                1
              </span>
              <span>
                Go to <strong>Atlassian Account Settings</strong> (
                <a
                  href="https://id.atlassian.com/manage-profile/security/api-tokens"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  id.atlassian.com
                </a>
                )
              </span>
            </li>
            <li className="flex gap-4">
              <span className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                2
              </span>
              <span>Click on "Create API token"</span>
            </li>
            <li className="flex gap-4">
              <span className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                3
              </span>
              <span>Give it a label (e.g., "Requirement Analyzer")</span>
            </li>
            <li className="flex gap-4">
              <span className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                4
              </span>
              <span>Copy the token and paste it in the API Token field above</span>
            </li>
            <li className="flex gap-4">
              <span className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                5
              </span>
              <span>
                Your Project Key can be found in Jira URL: https://your-domain.atlassian.net/jira/c/projects/
                <strong>PROJ</strong>
              </span>
            </li>
          </ol>
        </div>
      </div>
    </div>
  );
}
