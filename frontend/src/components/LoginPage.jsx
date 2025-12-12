import { useState, useRef } from "react";
import axios from "axios";
import { Toast } from "primereact/toast";
import { FaCheckCircle, FaTimesCircle } from "react-icons/fa";

const API_BASE = "http://localhost:8000";

export default function LoginPage({ setIsAuthenticated, setUser }) {
  const toast = useRef(null);
  const [isLogin, setIsLogin] = useState(true);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const endpoint = isLogin ? "/api/auth/login" : "/api/auth/register";
      const payload = isLogin ? { email, password } : { name, email, password };
      
      console.log(`Attempting ${isLogin ? "login" : "registration"}:`, { email, hasPassword: !!password });
      
      const response = await axios.post(`${API_BASE}${endpoint}`, payload);

      console.log("Authentication successful:", { email, token: response.data.access_token?.substring(0, 20) + "..." });

      if (response.data.access_token) {
        // Store token in localStorage
        localStorage.setItem("token", response.data.access_token);
        localStorage.setItem("email", email);
        if (!isLogin) {
          localStorage.setItem("name", name);
        }

        // Show success message
      toast.current.show({
        severity: "success",
        summary: "Success",
        detail: `${isLogin ? "Login" : "Registration"} successful! Redirecting...`,
        life: 2000,
      });        // Update auth state - this will trigger App.jsx to re-render
        setTimeout(() => {
          setIsAuthenticated(true);
          setUser({ name: name || email.split("@")[0], email });
        }, 1000);
      }
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 
        err.message ||
        `${isLogin ? "Login" : "Registration"} failed. Please try again.`;
      
      console.error("Authentication error:", {
        status: err.response?.status,
        message: errorMessage,
        data: err.response?.data,
        fullError: err
      });
      
      toast.current.show({
        severity: "error",
        summary: "Error",
        detail: errorMessage,
        life: 2000,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 to-purple-700 flex items-center justify-center p-4">
      <Toast 
        ref={toast} 
        position="top-center"
        className="custom-toast"
      />
      
      <div className="w-full max-w-md">
        {/* Logo/Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Requirement Analyzer</h1>
          <p className="text-blue-100">Agentic AI System</p>
        </div>

        {/* Form Card */}
        <div className="bg-white rounded-lg shadow-xl p-8">
          {/* Tabs */}
          <div className="flex gap-4 mb-6 border-b">
            <button
              onClick={() => {
                setIsLogin(true);
                setError("");
                setName("");
              }}
              className={`flex-1 py-3 font-semibold transition-colors ${
                isLogin
                  ? "text-blue-600 border-b-2 border-blue-600"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              Login
            </button>
            <button
              onClick={() => {
                setIsLogin(false);
                setError("");
                setName("");
              }}
              className={`flex-1 py-3 font-semibold transition-colors ${
                !isLogin
                  ? "text-blue-600 border-b-2 border-blue-600"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              Register
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Name - Only show for registration */}
            {!isLogin && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Full Name
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="John Doe"
                  required={!isLogin}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                />
              </div>
            )}

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
              />
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold py-2 rounded-lg hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "Please wait..." : isLogin ? "Login" : "Create Account"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
