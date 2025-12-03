import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginUser, registerUser, setAuthToken } from "../api/api";
import { FaEnvelope, FaLock, FaUser, FaSpinner } from "react-icons/fa";

export default function LoginPage({ setIsAuthenticated }) {
  const navigate = useNavigate();
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [testingConnection, setTestingConnection] = useState(false);
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    fullName: "",
  });

  const testBackendConnection = async () => {
    setTestingConnection(true);
    try {
      const response = await fetch("http://localhost:8000/health", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        alert(`✓ Backend is running!\nResponse: ${JSON.stringify(data)}`);
      } else {
        alert(`✗ Backend responded with status: ${response.status}`);
      }
    } catch (err) {
      alert(`✗ Cannot connect to backend: ${err.message}\n\nMake sure:\n1. Backend is running on http://localhost:8000\n2. PostgreSQL is running\n3. .env file has correct POSTGRES_URL`);
    } finally {
      setTestingConnection(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      let response;
      if (isLogin) {
        response = await loginUser(formData.email, formData.password);
      } else {
        response = await registerUser(
          formData.email,
          formData.password,
          formData.fullName
        );
      }

      const { access_token, refresh_token, user_id, email } = response.data;
      
      // Store tokens
      setAuthToken(access_token);
      localStorage.setItem("refresh_token", refresh_token);
      localStorage.setItem("user", JSON.stringify({ id: user_id, email }));

      // Update authentication state in parent component
      setIsAuthenticated(true);

      navigate("/");
    } catch (err) {
      console.error("Auth error:", err);
      console.error("Response data:", err.response?.data);
      console.error("Response status:", err.response?.status);
      console.error("Error message:", err.message);
      
      let errorMsg = "Authentication failed. Please try again.";
      if (err.response?.data?.detail) {
        errorMsg = err.response.data.detail;
      } else if (err.message === "Network Error" || !err.response) {
        errorMsg = "Cannot connect to server. Make sure the backend is running on http://localhost:8000";
      } else if (err.message) {
        errorMsg = err.message;
      }
      
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-2xl w-full max-w-md p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            {isLogin ? "Welcome Back" : "Create Account"}
          </h1>
          <p className="text-gray-600 mt-2">
            {isLogin
              ? "Sign in to access your requirements"
              : "Register to get started"}
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            <p className="font-semibold">Error</p>
            <p className="text-sm">{error}</p>
            <button
              type="button"
              onClick={testBackendConnection}
              disabled={testingConnection}
              className="mt-2 text-xs underline hover:font-bold"
            >
              {testingConnection ? "Testing..." : "Test backend connection"}
            </button>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <div className="relative">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Full Name
              </label>
              <div className="flex items-center border border-gray-300 rounded-lg px-3 py-2">
                <FaUser className="text-gray-400 mr-2" />
                <input
                  type="text"
                  name="fullName"
                  value={formData.fullName}
                  onChange={handleInputChange}
                  placeholder="John Doe"
                  required={!isLogin}
                  className="w-full outline-none text-gray-900"
                />
              </div>
            </div>
          )}

          <div className="relative">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <div className="flex items-center border border-gray-300 rounded-lg px-3 py-2">
              <FaEnvelope className="text-gray-400 mr-2" />
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="your@email.com"
                required
                className="w-full outline-none text-gray-900"
              />
            </div>
          </div>

          <div className="relative">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <div className="flex items-center border border-gray-300 rounded-lg px-3 py-2">
              <FaLock className="text-gray-400 mr-2" />
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                placeholder="••••••••"
                required
                minLength="6"
                className="w-full outline-none text-gray-900"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 disabled:opacity-50 text-white font-semibold py-2 rounded-lg transition flex items-center justify-center gap-2"
          >
            {loading && <FaSpinner className="animate-spin" />}
            {isLogin ? "Sign In" : "Create Account"}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-gray-600 text-sm">
            {isLogin ? "Don't have an account? " : "Already have an account? "}
            <button
              onClick={() => {
                setIsLogin(!isLogin);
                setError(null);
                setFormData({ email: "", password: "", fullName: "" });
              }}
              className="text-blue-500 hover:text-blue-700 font-semibold"
            >
              {isLogin ? "Sign Up" : "Sign In"}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
