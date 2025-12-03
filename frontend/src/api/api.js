// src/api/api.js
import axios from "axios";

const API_BASE = "http://localhost:8000";

export const api = axios.create({
  baseURL: API_BASE,
});

// Add token to all requests
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

// Handle 401 responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid, clear localStorage and redirect to login
      localStorage.removeItem("token");
      localStorage.removeItem("email");
      window.location.href = "/";
    }
    return Promise.reject(error);
  }
);

export const registerUser = (name, email, password) =>
  axios.post(`${API_BASE}/auth/register`, { name, email, password });

export const loginUser = (email, password) =>
  axios.post(`${API_BASE}/auth/login`, { email, password });

export const verifyToken = (token) =>
  api.post(`${API_BASE}/auth/verify-token?token=${token}`);

export const uploadFile = (file) => {
  const formData = new FormData();
  formData.append("file", file);
  const token = localStorage.getItem("token");
  return axios.post(`${API_BASE}/upload`, formData, {
    headers: {
      "Content-Type": "multipart/form-data",
      Authorization: `Bearer ${token}`,
    },
  });
};

export const fetchUploads = () =>
  api.get(`${API_BASE}/list-files`);

// Generation endpoints (POST)
export const generateEpics = (uploadId) =>
  api.post(`${API_BASE}/generate-epics/${uploadId}`);

export const generateStories = (epicId) =>
  api.post(`${API_BASE}/generate-stories/${epicId}`);

export const generateQA = (storyId) =>
  api.post(`${API_BASE}/generate-qa/${storyId}`);

// GET Endpoints for hierarchical data
export const fetchEpicsByUpload = (uploadId) => 
  api.get(`${API_BASE}/epics/${uploadId}`);

export const fetchAllEpics = (page = 1, page_size = 10, sort_by = "created_at", sort_order = "desc") =>
  api.get(`${API_BASE}/epics`, { params: { page, page_size, sort_by, sort_order } });

export const fetchEpicDetails = (uploadId, epicId) => 
  api.get(`${API_BASE}/epics/${uploadId}/${epicId}`);

export const fetchStoriesByEpic = (epicId) => 
  api.get(`${API_BASE}/stories/${epicId}`);

export const fetchAllStories = (page = 1, page_size = 10, sort_by = "created_at", sort_order = "desc") =>
  api.get(`${API_BASE}/stories`, { params: { page, page_size, sort_by, sort_order } });

export const fetchStoryDetails = (epicId, storyId) => 
  api.get(`${API_BASE}/stories/${epicId}/${storyId}`);

export const fetchQAByStory = (storyId) => 
  api.get(`${API_BASE}/qa/${storyId}`);

export const fetchAllQA = (page = 1, page_size = 10, sort_by = "created_at", sort_order = "desc") =>
  api.get(`${API_BASE}/qa`, { params: { page, page_size, sort_by, sort_order } });

export const fetchQADetails = (storyId, qaId) => 
  api.get(`${API_BASE}/qa/${storyId}/${qaId}`);

export const fetchTestPlansByEpic = (epicId) => 
  api.get(`${API_BASE}/testplans/${epicId}`);

export const fetchAllTestPlans = (page = 1, page_size = 10, sort_by = "created_at", sort_order = "desc") =>
  api.get(`${API_BASE}/testplans`, { params: { page, page_size, sort_by, sort_order } });

export const fetchTestPlanDetails = (epicId, testplanId) => 
  api.get(`${API_BASE}/testplans/${epicId}/${testplanId}`);
