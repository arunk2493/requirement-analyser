// src/api/api.js
import axios from "axios";

const API_BASE = "http://localhost:8000";

export const api = axios.create({
  baseURL: API_BASE,
});

// Token management
export const setAuthToken = (token) => {
  if (token) {
    api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    localStorage.setItem("token", token);
  }
};

export const clearAuthToken = () => {
  delete api.defaults.headers.common["Authorization"];
  localStorage.removeItem("token");
  localStorage.removeItem("user");
};

// Initialize token from localStorage on app load
export const initializeAuthToken = () => {
  const token = localStorage.getItem("token");
  if (token) {
    api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
  }
};

// Request interceptor to add token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle 401 and refresh token
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem("refresh_token");
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE}/auth/refresh-token`, {
            refresh_token: refreshToken,
          });
          const { access_token, refresh_token: newRefreshToken } = response.data;
          setAuthToken(access_token);
          localStorage.setItem("refresh_token", newRefreshToken);
          return api(originalRequest);
        } catch (refreshError) {
          clearAuthToken();
          window.location.href = "/login";
          return Promise.reject(refreshError);
        }
      }
    }
    return Promise.reject(error);
  }
);

// Auth endpoints - use plain axios for auth since no token yet
export const registerUser = (email, password, fullName) =>
  axios.post(`${API_BASE}/auth/register`, {
    email,
    password,
    full_name: fullName,
  });

export const loginUser = (email, password) =>
  axios.post(`${API_BASE}/auth/login`, {
    email,
    password,
  });

export const getCurrentUser = () =>
  api.get(`/auth/me`);

export const uploadFile = (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return api.post(`/upload`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const fetchUploads = () =>
  api.get(`/uploads`);

// Generation endpoints (POST) - Using Agentic AI endpoints
export const generateEpics = (uploadId) =>
  api.post(`/agents/epic/generate`, {
    upload_id: uploadId
  });

export const generateStories = (epicId) =>
  api.post(`/agents/story/generate`, {
    epic_id: epicId
  });

export const generateQA = (storyId) =>
  api.post(`/agents/qa/generate`, {
    story_id: storyId
  });

export const generateTestPlan = (epicId) =>
  api.post(`/agents/testplan/generate`, {
    epic_id: epicId
  });

// GET Endpoints for hierarchical data
export const fetchEpicsByUpload = (uploadId) => 
  api.get(`/epics/${uploadId}`);

export const fetchAllEpics = (page = 1, page_size = 10, sort_by = "created_at", sort_order = "desc") =>
  api.get(`/epics`, { params: { page, page_size, sort_by, sort_order } });

export const fetchEpicDetails = (uploadId, epicId) => 
  api.get(`/epics/${uploadId}/${epicId}`);

export const fetchStoriesByEpic = (epicId) => 
  api.get(`/stories/${epicId}`);

export const fetchAllStories = (page = 1, page_size = 10, sort_by = "created_at", sort_order = "desc") =>
  api.get(`/stories`, { params: { page, page_size, sort_by, sort_order } });

export const fetchStoryDetails = (epicId, storyId) => 
  api.get(`/stories/${epicId}/${storyId}`);

export const fetchQAByStory = (storyId) => 
  api.get(`/qa/${storyId}`);

export const fetchAllQA = (page = 1, page_size = 10, sort_by = "created_at", sort_order = "desc") =>
  api.get(`/qa`, { params: { page, page_size, sort_by, sort_order } });

export const fetchQADetails = (storyId, qaId) => 
  api.get(`/qa/${storyId}/${qaId}`);

export const fetchTestPlansByEpic = (epicId) => 
  api.get(`/testplans/${epicId}`);

export const fetchAllTestPlans = (page = 1, page_size = 10, sort_by = "created_at", sort_order = "desc") =>
  api.get(`/testplans`, { params: { page, page_size, sort_by, sort_order } });

export const fetchTestPlanDetails = (epicId, testplanId) => 
  api.get(`/testplans/${epicId}/${testplanId}`);
