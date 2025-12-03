import axios from "axios";

const API_BASE = "http://localhost:8000";

// Create axios instance with token management
export const api = axios.create({
  baseURL: API_BASE,
});

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem("refresh_token");
        if (refreshToken) {
          const response = await axios.post(`${API_BASE}/auth/refresh`, {
            refresh_token: refreshToken,
          });
          localStorage.setItem("access_token", response.data.access_token);
          localStorage.setItem("refresh_token", response.data.refresh_token);
          originalRequest.headers.Authorization = `Bearer ${response.data.access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        globalThis.location.href = "/login";
      }
    }
    throw error;
  }
);

export const uploadFile = (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return api.post(`/upload`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const fetchUploads = () =>
  api.get(`/uploads`);

// Generation endpoints (POST)
export const generateEpics = (uploadId) =>
  api.post(`/generate-epics/${uploadId}`);

export const generateStories = (epicId) =>
  api.post(`/generate-stories/${epicId}`);

export const generateQA = (storyId) =>
  api.post(`/generate-qa/${storyId}`);

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

// Auth endpoints
export const register = (email, password, fullName) =>
  axios.post(`${API_BASE}/auth/register`, {
    email,
    password,
    full_name: fullName,
  });

export const login = (email, password) =>
  axios.post(`${API_BASE}/auth/login`, {
    email,
    password,
  });



export const getCurrentUser = () =>
  api.get(`/auth/me`, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem("access_token")}`,
    },
  });

export const logout = () => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("user");
};
