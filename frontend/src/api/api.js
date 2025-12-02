// src/api/api.js
import axios from "axios";

const API_BASE = "http://localhost:8000";

export const api = axios.create({
  baseURL: API_BASE,
});

export const uploadFile = (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return axios.post(`${API_BASE}/upload`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const fetchUploads = () =>
  axios.get(`${API_BASE}/list-files`);

// Generation endpoints (POST)
export const generateEpics = (uploadId) =>
  axios.post(`${API_BASE}/generate-epics/${uploadId}`);

export const generateStories = (epicId) =>
  axios.post(`${API_BASE}/generate-stories/${epicId}`);

export const generateQA = (storyId) =>
  axios.post(`${API_BASE}/generate-qa/${storyId}`);

// GET Endpoints for hierarchical data
export const fetchEpicsByUpload = (uploadId) => 
  axios.get(`${API_BASE}/epics/${uploadId}`);

export const fetchAllEpics = (page = 1, page_size = 10, sort_by = "created_at", sort_order = "desc") =>
  axios.get(`${API_BASE}/epics`, { params: { page, page_size, sort_by, sort_order } });

export const fetchEpicDetails = (uploadId, epicId) => 
  axios.get(`${API_BASE}/epics/${uploadId}/${epicId}`);

export const fetchStoriesByEpic = (epicId) => 
  axios.get(`${API_BASE}/stories/${epicId}`);

export const fetchAllStories = (page = 1, page_size = 10, sort_by = "created_at", sort_order = "desc") =>
  axios.get(`${API_BASE}/stories`, { params: { page, page_size, sort_by, sort_order } });

export const fetchStoryDetails = (epicId, storyId) => 
  axios.get(`${API_BASE}/stories/${epicId}/${storyId}`);

export const fetchQAByStory = (storyId) => 
  axios.get(`${API_BASE}/qa/${storyId}`);

export const fetchAllQA = (page = 1, page_size = 10, sort_by = "created_at", sort_order = "desc") =>
  axios.get(`${API_BASE}/qa`, { params: { page, page_size, sort_by, sort_order } });

export const fetchQADetails = (storyId, qaId) => 
  axios.get(`${API_BASE}/qa/${storyId}/${qaId}`);

export const fetchTestPlansByEpic = (epicId) => 
  axios.get(`${API_BASE}/testplans/${epicId}`);

export const fetchAllTestPlans = (page = 1, page_size = 10, sort_by = "created_at", sort_order = "desc") =>
  axios.get(`${API_BASE}/testplans`, { params: { page, page_size, sort_by, sort_order } });

export const fetchTestPlanDetails = (epicId, testplanId) => 
  axios.get(`${API_BASE}/testplans/${epicId}/${testplanId}`);
