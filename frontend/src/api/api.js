// src/api/api.js
import axios from "axios";

const API_BASE = "http://localhost:5000/api";

export const api = axios.create({
  baseURL: "http://localhost:5000",
});

export const uploadFile = (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return axios.post(`${API_BASE}/upload`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const fetchDashboard = () => axios.get(`${API_BASE}/api/data`);
export const fetchEpics = () => axios.get(`${API_BASE}/api/epics`);
export const fetchStories = () => axios.get(`${API_BASE}/api/stories`);
export const fetchQA = () => axios.get(`${API_BASE}/api/qa`);
