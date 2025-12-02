import { useEffect, useState } from "react";
import {
  fetchUploads,
  generateEpics,
  generateStories,
  generateQA,
  fetchAllEpics,
  fetchAllStories,
  fetchAllQA,
  fetchAllTestPlans,
} from "../api/api";
import { FaFileAlt, FaSpinner, FaBolt } from "react-icons/fa";

export default function GenerateConfluence() {
  const [uploads, setUploads] = useState([]);
  const [selectedUpload, setSelectedUpload] = useState(null);
  const [selectedEpic, setSelectedEpic] = useState(null);
  const [selectedStory, setSelectedStory] = useState(null);

  const [loadingUploads, setLoadingUploads] = useState(false);
  const [busy, setBusy] = useState(false);

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
      // preselect first upload if available
      if ((res.data.uploads || []).length > 0 && !selectedUpload) {
        setSelectedUpload(res.data.uploads[0].upload_id);
      }
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

  // helper to refresh everything after create
  const refreshAll = async () => {
    await Promise.all([loadUploads(), loadRecentLists()]);
  };

  const onGenerateEpics = async () => {
    if (!selectedUpload) return;
    try {
      setBusy(true);
      await generateEpics(selectedUpload);
      await refreshAll();
    } catch (e) {
      console.error("generate epics failed", e.response || e);
      alert("Failed to generate epics: " + (e.response?.data?.detail || e.message || e));
    } finally {
      setBusy(false);
    }
  };

  const onGenerateStories = async () => {
    if (!selectedEpic) return;
    try {
      setBusy(true);
      await generateStories(selectedEpic);
      await refreshAll();
    } catch (e) {
      console.error("generate stories failed", e.response || e);
      alert("Failed to generate stories: " + (e.response?.data?.detail || e.message || e));
    } finally {
      setBusy(false);
    }
  };

  const onGenerateQA = async () => {
    if (!selectedStory) return;
    try {
      setBusy(true);
      await generateQA(selectedStory);
      await refreshAll();
    } catch (e) {
      console.error("generate qa failed", e.response || e);
      alert("Failed to generate QA: " + (e.response?.data?.detail || e.message || e));
    } finally {
      setBusy(false);
    }
  };

  // compute list of epics/stories for selects from uploads
  const allEpics = [];
  uploads.forEach((u) => {
    (u.epics || []).forEach((e) => allEpics.push({ upload_id: u.upload_id, epic_id: e.epic_id, name: e.name }));
  });

  const allStories = [];
  uploads.forEach((u) => {
    (u.epics || []).forEach((e) => {
      (e.stories || []).forEach((s) => allStories.push({ epic_id: e.epic_id, story_id: s.story_id, name: s.name }));
    });
  });

  return (
    <div className="min-h-screen p-8 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <div className="mb-8 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <FaFileAlt className="text-4xl text-indigo-600" />
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Generate Confluence Documents</h1>
        </div>
        <div className="text-sm text-gray-600 dark:text-gray-400">Generate Epics, Stories, and QA and view recent items</div>
      </div>

      <div className="grid grid-cols-12 gap-6">
        {/* Left: controls */}
        <div className="col-span-5 bg-white dark:bg-gray-800 rounded-lg p-6 shadow">
          <h2 className="text-lg font-semibold mb-4">Generate Content</h2>

          <div className="mb-4">
            <label className="block text-sm text-gray-700 dark:text-gray-300 mb-2">Select Upload (for Epics)</label>
            {loadingUploads ? (
              <div className="flex items-center gap-2 text-sm"><FaSpinner className="animate-spin"/> Loading uploads...</div>
            ) : (
              <select value={selectedUpload || ""} onChange={(e) => setSelectedUpload(Number(e.target.value) || null)} className="w-full p-2 border rounded">
                <option value="">-- choose upload --</option>
                {uploads.map((u) => (
                  <option key={u.upload_id} value={u.upload_id}>{u.name || `Upload ${u.upload_id}`}</option>
                ))}
              </select>
            )}
            <div className="mt-3">
              <button disabled={!selectedUpload || busy} onClick={onGenerateEpics} className="px-4 py-2 bg-indigo-600 text-white rounded disabled:opacity-50">
                {busy ? <><FaSpinner className="inline animate-spin mr-2"/>Generating...</> : <>Generate Epics</>}
              </button>
            </div>
          </div>

          <hr className="my-4" />

          <div className="mb-4">
            <label className="block text-sm text-gray-700 dark:text-gray-300 mb-2">Select Epic (for Stories)</label>
            <select value={selectedEpic || ""} onChange={(e) => setSelectedEpic(Number(e.target.value) || null)} className="w-full p-2 border rounded">
              <option value="">-- choose epic --</option>
              {allEpics.map((e) => (
                <option key={e.epic_id} value={e.epic_id}>{e.name || `Epic ${e.epic_id}`}</option>
              ))}
            </select>
            <div className="mt-3">
              <button disabled={!selectedEpic || busy} onClick={onGenerateStories} className="px-4 py-2 bg-green-600 text-white rounded disabled:opacity-50">
                {busy ? <><FaSpinner className="inline animate-spin mr-2"/>Generating...</> : <>Generate Stories</>}
              </button>
            </div>
          </div>

          <hr className="my-4" />

          <div>
            <label className="block text-sm text-gray-700 dark:text-gray-300 mb-2">Select Story (for QA)</label>
            <select value={selectedStory || ""} onChange={(e) => setSelectedStory(Number(e.target.value) || null)} className="w-full p-2 border rounded">
              <option value="">-- choose story --</option>
              {allStories.map((s) => (
                <option key={s.story_id} value={s.story_id}>{s.name || `Story ${s.story_id}`}</option>
              ))}
            </select>
            <div className="mt-3">
              <button disabled={!selectedStory || busy} onClick={onGenerateQA} className="px-4 py-2 bg-yellow-600 text-white rounded disabled:opacity-50">
                {busy ? <><FaSpinner className="inline animate-spin mr-2"/>Generating...</> : <>Generate QA</>}
              </button>
            </div>
          </div>
        </div>

        {/* Right: recent items */}
        <div className="col-span-7 space-y-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow">
            <h3 className="font-semibold mb-3">Recent Epics</h3>
            {recentEpics.length === 0 ? <div className="text-sm text-gray-500">No epics yet</div> : (
              <ul className="divide-y">
                {recentEpics.map((e) => (
                  <li key={e.id} className="py-2 flex justify-between items-start">
                    <div>
                      <div className="font-medium">{e.name || `Epic ${e.id}`}</div>
                      <div className="text-sm text-gray-500">Created: {new Date(e.created_at).toLocaleString()}</div>
                    </div>
                    <div>
                      {e.confluence_page_url ? <a className="text-indigo-600" target="_blank" rel="noreferrer" href={e.confluence_page_url}>View</a> : null}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow">
              <h3 className="font-semibold mb-3">Recent Stories</h3>
              {recentStories.length === 0 ? <div className="text-sm text-gray-500">No stories yet</div> : (
                <ul className="divide-y">
                  {recentStories.map((s) => (
                    <li key={s.id} className="py-2">
                      <div className="font-medium">{s.name || `Story ${s.id}`}</div>
                      <div className="text-sm text-gray-500">Created: {new Date(s.created_at).toLocaleString()}</div>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow">
              <h3 className="font-semibold mb-3">Recent QA</h3>
              {recentQA.length === 0 ? <div className="text-sm text-gray-500">No QA yet</div> : (
                <ul className="divide-y">
                  {recentQA.map((q) => (
                    <li key={q.id} className="py-2">
                      <div className="font-medium">QA #{q.id}</div>
                      <div className="text-sm text-gray-500">Created: {new Date(q.created_at).toLocaleString()}</div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow">
            <h3 className="font-semibold mb-3">Recent Test Plans</h3>
            {recentTestPlans.length === 0 ? <div className="text-sm text-gray-500">No test plans yet</div> : (
              <ul className="divide-y">
                {recentTestPlans.map((t) => (
                  <li key={t.id} className="py-2 flex justify-between items-start">
                    <div>
                      <div className="font-medium">{t.title || `Test Plan ${t.id}`}</div>
                      <div className="text-sm text-gray-500">Created: {new Date(t.created_at).toLocaleString()}</div>
                    </div>
                    <div>
                      {t.confluence_page_url ? <a className="text-indigo-600" target="_blank" rel="noreferrer" href={t.confluence_page_url}>View</a> : null}
                    </div>
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
