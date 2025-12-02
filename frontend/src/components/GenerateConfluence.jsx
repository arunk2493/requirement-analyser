import { useEffect, useState } from "react";
import {
  fetchUploads,
  generateEpics,
  generateStories,
  generateQA,
  fetchAllEpics,
  fetchAllStories,
  fetchAllQA,
  fetchAllTestPlans
} from "../api/api";

import { FaFileAlt, FaSpinner } from "react-icons/fa";

export default function GenerateConfluence() {
  const [uploads, setUploads] = useState([]);

  // Text inputs
  const [uploadIdInput, setUploadIdInput] = useState("");
  const [epicIdInput, setEpicIdInput] = useState("");
  const [storyIdInput, setStoryIdInput] = useState("");

  // Individual button loading states
  const [loadingEpics, setLoadingEpics] = useState(false);
  const [loadingStories, setLoadingStories] = useState(false);
  const [loadingQA, setLoadingQA] = useState(false);

  const [loadingUploads, setLoadingUploads] = useState(false);

  // Notification banner
  const [notification, setNotification] = useState({ type: "", message: "" });

  const showNotification = (type, message) => {
    setNotification({ type, message });
    setTimeout(() => setNotification({ type: "", message: "" }), 4000);
  };

  // Recent lists
  const [recentEpics, setRecentEpics] = useState([]);
  const [recentStories, setRecentStories] = useState([]);
  const [recentQA, setRecentQA] = useState([]);
  const [recentTestPlans, setRecentTestPlans] = useState([]);

  const pageSize = 5;

  const loadUploads = async () => {
    try {
      setLoadingUploads(true);
      const res = await fetchUploads();
      setUploads(res.data.uploads || []);
    } catch (e) {
      console.error("Could not load uploads", e);
    } finally {
      setLoadingUploads(false);
    }
  };

  const loadRecentLists = async () => {
    try {
      const [epRes, stRes, qaRes, tpRes] = await Promise.all([
        fetchAllEpics(1, pageSize),
        fetchAllStories(1, pageSize),
        fetchAllQA(1, pageSize),
        fetchAllTestPlans(1, pageSize),
      ]);

      setRecentEpics(epRes.data.epics || []);
      setRecentStories(stRes.data.stories || []);
      setRecentQA(qaRes.data.qa_tests || []);
      setRecentTestPlans(tpRes.data.test_plans || []);
    } catch (e) {
      console.error("Failed to load recent lists", e);
    }
  };

  useEffect(() => {
    loadUploads();
    loadRecentLists();
  }, []);

  const refreshAll = async () => {
    await Promise.all([loadUploads(), loadRecentLists()]);
  };

  // Generate Epics
  const onGenerateEpics = async () => {
    if (!uploadIdInput) return showNotification("error", "Upload ID is required");

    try {
      setLoadingEpics(true);
      await generateEpics(Number(uploadIdInput));
      showNotification("success", "Epics generated successfully");
      await refreshAll();
    } catch (e) {
      showNotification("error", e.response?.data?.detail || "Failed to generate epics");
    } finally {
      setLoadingEpics(false);
    }
  };

  // Generate Stories
  const onGenerateStories = async () => {
    if (!epicIdInput) return showNotification("error", "Epic ID is required");

    try {
      setLoadingStories(true);
      await generateStories(Number(epicIdInput));
      showNotification("success", "Stories generated successfully");
      await refreshAll();
    } catch (e) {
      showNotification("error", e.response?.data?.detail || "Failed to generate stories");
    } finally {
      setLoadingStories(false);
    }
  };

  // Generate QA
  const onGenerateQA = async () => {
    if (!storyIdInput) return showNotification("error", "Story ID is required");

    try {
      setLoadingQA(true);
      await generateQA(Number(storyIdInput));
      showNotification("success", "QA generated successfully");
      await refreshAll();
    } catch (e) {
      showNotification("error", e.response?.data?.detail || "Failed to generate QA");
    } finally {
      setLoadingQA(false);
    }
  };

  return (
    <div className="min-h-screen p-8 bg-gray-100">

      {/* Notification Banner */}
      {notification.message && (
        <div
          className={`p-3 mb-4 rounded text-white ${
            notification.type === "success" ? "bg-green-600" : "bg-red-600"
          }`}
        >
          {notification.message}
        </div>
      )}

      <div className="mb-8 flex items-center gap-3">
        <FaFileAlt className="text-4xl text-indigo-600" />
        <h1 className="text-3xl font-bold">Generate Confluence Documents</h1>
      </div>

      <div className="grid grid-cols-12 gap-6">
        {/* LEFT PANEL — INPUTS */}
        <div className="col-span-5 bg-white rounded-lg p-6 shadow">
          <h2 className="text-lg font-semibold mb-4">Generate Content</h2>

          {/* Upload ID */}
          <label className="block mb-1 text-sm">Upload ID (for Epics)</label>
          <input
            type="text"
            value={uploadIdInput}
            onChange={(e) => setUploadIdInput(e.target.value)}
            placeholder="Enter Upload ID"
            className="w-full p-2 border rounded"
          />
          <button
            disabled={loadingEpics}
            onClick={onGenerateEpics}
            className="mt-3 w-full px-4 py-2 bg-indigo-600 text-white rounded disabled:opacity-50"
          >
            {loadingEpics ? (
              <><FaSpinner className="inline animate-spin mr-2" />Generating...</>
            ) : (
              "Generate Epics"
            )}
          </button>

          <hr className="my-4" />

          {/* Epic ID */}
          <label className="block mb-1 text-sm">Epic ID (for Stories)</label>
          <input
            type="text"
            value={epicIdInput}
            onChange={(e) => setEpicIdInput(e.target.value)}
            placeholder="Enter Epic ID"
            className="w-full p-2 border rounded"
          />
          <button
            disabled={loadingStories}
            onClick={onGenerateStories}
            className="mt-3 w-full px-4 py-2 bg-green-600 text-white rounded disabled:opacity-50"
          >
            {loadingStories ? (
              <><FaSpinner className="inline animate-spin mr-2" />Generating...</>
            ) : (
              "Generate Stories"
            )}
          </button>

          <hr className="my-4" />

          {/* Story ID */}
          <label className="block mb-1 text-sm">Story ID (for QA)</label>
          <input
            type="text"
            value={storyIdInput}
            onChange={(e) => setStoryIdInput(e.target.value)}
            placeholder="Enter Story ID"
            className="w-full p-2 border rounded"
          />
          <button
            disabled={loadingQA}
            onClick={onGenerateQA}
            className="mt-3 w-full px-4 py-2 bg-yellow-600 text-white rounded disabled:opacity-50"
          >
            {loadingQA ? (
              <><FaSpinner className="inline animate-spin mr-2" />Generating...</>
            ) : (
              "Generate QA"
            )}
          </button>
        </div>

        {/* RIGHT PANEL — RECENT ITEMS */}
        <div className="col-span-7 space-y-4">

          {/* Recent Epics */}
          <div className="bg-white rounded-lg p-4 shadow">
            <h3 className="font-semibold mb-3">Recent Epics</h3>
            {recentEpics.length === 0 ? (
              <div>No epics yet</div>
            ) : (
              <ul className="divide-y">
                {recentEpics.map((e) => (
                  <li key={e.id} className="py-2 flex justify-between">
                    <div className="font-medium">{e.name}</div>
                    {e.confluence_page_url && (
                      <a className="text-indigo-600" target="_blank" href={e.confluence_page_url}>View</a>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">

            {/* Recent Stories */}
            <div className="bg-white rounded-lg p-4 shadow">
              <h3 className="font-semibold mb-3">Recent Stories</h3>
              {recentStories.length === 0 ? (
                <div>No stories yet</div>
              ) : (
                <ul className="divide-y">
                  {recentStories.map((s) => (
                    <li key={s.id} className="py-2 font-medium">
                      {s.name}
                    </li>
                  ))}
                </ul>
              )}
            </div>

            {/* Recent QA */}
            <div className="bg-white rounded-lg p-4 shadow">
              <h3 className="font-semibold mb-3">Recent QA</h3>
              {recentQA.length === 0 ? (
                <div>No QA yet</div>
              ) : (
                <ul className="divide-y">
                  {recentQA.map((q) => (
                    <li key={q.id} className="py-2 font-medium">
                      QA #{q.id}
                    </li>
                  ))}
                </ul>
              )}
            </div>

          </div>

          {/* Recent Test Plans */}
          <div className="bg-white rounded-lg p-4 shadow">
            <h3 className="font-semibold mb-3">Recent Test Plans</h3>
            {recentTestPlans.length === 0 ? (
              <div>No test plans yet</div>
            ) : (
              <ul className="divide-y">
                {recentTestPlans.map((t) => (
                  <li key={t.id} className="py-2 flex justify-between">
                    <div className="font-medium">{t.title}</div>
                    {t.confluence_page_url && (
                      <a className="text-indigo-600" target="_blank" href={t.confluence_page_url}>View</a>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}