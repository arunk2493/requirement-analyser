// src/api/api.js
import axios from "axios";

const API_BASE = "http://localhost:8000";

export const api = axios.create({
  baseURL: API_BASE,
});

// Add token to all requests with Bearer scheme
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

// Handle 401 responses - token expired or invalid
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid, clear localStorage and redirect to login
      console.error("Authentication failed:", error.response?.data?.detail);
      localStorage.removeItem("token");
      localStorage.removeItem("email");
      localStorage.removeItem("user_id");
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

export const fetchUploads = (page = 1, page_size = 100) =>
  api.get(`${API_BASE}/uploads`, { params: { page, page_size } });

// ============================================
// AGENTIC GENERATION ENDPOINTS (POST)
// All require Bearer token in Authorization header
// ============================================

export const generateEpicsAgent = (uploadId) =>
  api.post(`${API_BASE}/agents/epic/generate`, { upload_id: uploadId });

export const generateStoriesAgent = (epicId) =>
  api.post(`${API_BASE}/agents/story/generate`, { epic_id: epicId });

export const generateQAAgent = (storyId) =>
  api.post(`${API_BASE}/agents/qa/generate`, { story_id: storyId });

export const generateTestPlanAgent = (epicId) =>
  api.post(`${API_BASE}/agents/testplan/generate`, { epic_id: epicId });

export const executeWorkflow = (uploadId) =>
  api.post(`${API_BASE}/agents/workflow/execute`, { upload_id: uploadId });

// ============================================
// AGENTIC RETRIEVAL ENDPOINTS (GET)
// All require Bearer token in Authorization header
// ============================================

export const getEpicsAgent = (uploadId) =>
  api.get(`${API_BASE}/agents/epic/list`, { params: { upload_id: uploadId } });

export const getStoriesAgent = (epicId) =>
  api.get(`${API_BASE}/agents/story/list`, { params: { epic_id: epicId } });

export const getQAAgent = (storyId) =>
  api.get(`${API_BASE}/agents/qa/list`, { params: { story_id: storyId } });

export const getTestPlanAgent = (epicId) =>
  api.get(`${API_BASE}/agents/testplan/list`, { params: { epic_id: epicId } });

export const ragSearch = (query, uploadId, topK = 5) =>
  api.post(`${API_BASE}/agents/rag/search`, { 
    query, 
    upload_id: uploadId, 
    top_k: topK 
  });

export const ragVectorStoreSearch = (query, topK = 5) =>
  api.get(`${API_BASE}/rag/vectorstore-search`, { 
    params: {
      query, 
      top_k: topK 
    }
  });

// ============================================
// LEGACY GENERATION ENDPOINTS (POST)
// All require Bearer token in Authorization header
// ============================================

export const generateEpics = (uploadId) =>
  api.post(`${API_BASE}/generate-epics/${uploadId}`);

export const generateStories = (epicId) =>
  api.post(`${API_BASE}/generate-stories/${epicId}`);

export const generateQA = (storyId) =>
  api.post(`${API_BASE}/generate-qa/${storyId}`);

export const generateTestPlan = (storyId) =>
  api.post(`${API_BASE}/generate-testplan/${storyId}`);

// ============================================
// LEGACY DATA ENDPOINTS (GET)
// All require Bearer token in Authorization header
// ============================================
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
