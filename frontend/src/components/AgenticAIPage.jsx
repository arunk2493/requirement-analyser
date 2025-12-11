import { useState, useEffect, useRef } from "react";
import { generateEpicsAgent, generateStoriesAgent, generateQAAgent, generateTestPlanAgent, ragSearch, ragVectorStoreSearch, fetchUploads, getEpicsAgent, getStoriesAgent, getQAAgent, getTestPlanAgent } from "../api/api";
import { FaRobot, FaSpinner, FaExternalLinkAlt, FaSync, FaCheckCircle, FaTimesCircle, FaArrowRight, FaJira } from "react-icons/fa";
import { Toast } from "primereact/toast";
import { Dropdown } from "primereact/dropdown";
import { Button } from "primereact/button";
import { Accordion, AccordionTab } from "primereact/accordion";
import { DataTable } from "primereact/datatable";
import { Column } from "primereact/column";

const API_BASE_URL = "http://localhost:8000";

/**
 * AgenticAIPage Component
 * 
 * Main page for generating epics, stories, QA tests, and test plans using AI agents.
 * Features:
 * - Upload selection and management
 * - Epic generation and Jira integration
 * - Story generation with parent epic linking
 * - QA test generation for stories
 * - Test plan generation for epics
 * - RAG-based document search
 * - Real-time progress tracking
 * - Error handling and retry mechanisms
 */
export default function AgenticAIPage() {
  // ============================================================================
  // Toast Reference for Notifications
  // ============================================================================
  const toast = useRef(null);

  // ============================================================================
  // STATE MANAGEMENT - Selection State
  // ============================================================================
  const [uploadId, setUploadId] = useState("");
  const [epicIdForStories, setEpicIdForStories] = useState("");
  const [epicIdForTestPlan, setEpicIdForTestPlan] = useState("");
  const [storyId, setStoryId] = useState("");
  const [ragQuery, setRagQuery] = useState("");

  // ============================================================================
  // STATE MANAGEMENT - Data State
  // ============================================================================
  const [userUploads, setUserUploads] = useState([]);
  const [loadingUploads, setLoadingUploads] = useState(true);
  
  const [loadingEpics, setLoadingEpics] = useState(false);
  const [loadingStories, setLoadingStories] = useState(false);
  const [loadingQA, setLoadingQA] = useState(false);
  const [loadingTestPlan, setLoadingTestPlan] = useState(false);
  const [loadingRAG, setLoadingRAG] = useState(false);

  // ============================================================================
  // STATE MANAGEMENT - Progress Tracking
  // ============================================================================
  const [epicProgress, setEpicProgress] = useState(0);
  const [storyProgress, setStoryProgress] = useState(0);
  const [qaProgress, setQAProgress] = useState(0);
  const [testPlanProgress, setTestPlanProgress] = useState(0);
  const [uploadProgress, setUploadProgress] = useState(0);

  // ============================================================================
  // STATE MANAGEMENT - Generated Content
  // ============================================================================
  const [generatedEpics, setGeneratedEpics] = useState([]);
  const [generatedStories, setGeneratedStories] = useState([]);
  const [generatedQA, setGeneratedQA] = useState([]);
  const [generatedTestPlans, setGeneratedTestPlans] = useState([]);
  const [ragResults, setRagResults] = useState([]);

  // ============================================================================
  // STATE MANAGEMENT - Recent Items for Quick Access
  // ============================================================================
  const [recentEpics, setRecentEpics] = useState([]);
  const [recentStories, setRecentStories] = useState([]);
  const [recentQA, setRecentQA] = useState([]);
  const [recentUploads, setRecentUploads] = useState([]);

  // ============================================================================
  // STATE MANAGEMENT - Messaging
  // ============================================================================
  // Removed: successMessage and errorMessage states - now using Toast instead

  // ============================================================================
  // STATE MANAGEMENT - Jira Integration
  // ============================================================================
  const [jiraCredentials, setJiraCredentials] = useState(null);
  const [loadingJiraItems, setLoadingJiraItems] = useState(new Set()); // Track loading per item
  const [jiraResults, setJiraResults] = useState({});

  // ============================================================================
  // STATE MANAGEMENT - QA Regeneration Tracking
  // ============================================================================
  const [qaRegenerationAttempts, setQaRegenerationAttempts] = useState({}); // Track attempts per story

  // ============================================================================
  // LIFECYCLE HOOKS - Initialize Component
  // ============================================================================
  // Fetch user's uploads on component mount and when user logs in
  useEffect(() => {
    const fetchUserUploads = async () => {
      try {
        setLoadingUploads(true);
        const res = await fetchUploads();
        setUserUploads(res.data.uploads || []);
      } catch (error) {
        console.error("Failed to fetch uploads:", error);
        setUserUploads([]);
      } finally {
        setLoadingUploads(false);
      }
    };
    
    // Fetch immediately
    fetchUserUploads();

    // Clear all selections on component mount (fresh start)
    localStorage.removeItem("lastSelectedUploadId");
    localStorage.removeItem("lastSelectedEpicForStories");
    localStorage.removeItem("lastSelectedStoryId");
    localStorage.removeItem("lastSelectedEpicForTestPlan");
    
    // Listen for storage changes (user login from another tab/window)
    const handleStorageChange = (e) => {
      if (e.key === 'token' && e.newValue) {
        fetchUserUploads();
      }
    };
    
    window.addEventListener('storage', handleStorageChange);
    
    // Cleanup on unmount: clear all selections and generated data
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      // Clear selections on unmount
      localStorage.removeItem("lastSelectedUploadId");
      localStorage.removeItem("lastSelectedEpicForStories");
      localStorage.removeItem("lastSelectedStoryId");
      localStorage.removeItem("lastSelectedEpicForTestPlan");
    };
  }, []);

  // ============================================================================
  // LIFECYCLE HOOKS - Load Jira Credentials & Authentication
  // ============================================================================
  // Load Jira credentials from localStorage
  useEffect(() => {
    const savedJiraCredentials = localStorage.getItem("jira_credentials");
    if (savedJiraCredentials) {
      try {
        const parsed = JSON.parse(savedJiraCredentials);
        setJiraCredentials(parsed);
      } catch (e) {
        console.error("Failed to parse Jira credentials", e);
      }
    }
    
    // Clear user selections if user is not authenticated
    const token = localStorage.getItem("token");
    if (!token) {
      // Clear all saved selections when user logs out
      localStorage.removeItem("lastSelectedUploadId");
      localStorage.removeItem("lastSelectedEpicForStories");
      localStorage.removeItem("lastSelectedStoryId");
      localStorage.removeItem("lastSelectedEpicForTestPlan");
      
      // Reset state
      setUploadId("");
      setEpicIdForStories("");
      setStoryId("");
      setEpicIdForTestPlan("");
      setGeneratedEpics([]);
      setGeneratedStories([]);
      setGeneratedQA([]);
      setGeneratedTestPlans([]);
    }
  }, []);

  const showMessage = (type, message) => {
    if (type === "success") {
      toast.current.show({
        severity: "success",
        summary: "Success",
        detail: message,
        life: 2000,
      });
    } else if (type === "error") {
      toast.current.show({
        severity: "error",
        summary: "Error",
        detail: message,
        life: 2000,
      });
    } else {
      // warning
      toast.current.show({
        severity: "warn",
        summary: "Warning",
        detail: message,
        life: 2000,
      });
    }
  };

  const dismissError = () => {
    // Toast automatically dismisses, no need for manual dismiss
    return;
  };

  // Helper function to add item to recent list (keep only last 5, sorted by most recent first)
  const addToRecent = (setRecentFn, item, existingItems = []) => {
    // Create new item with timestamp
    const itemWithTime = { ...item, addedAt: new Date().getTime() };
    
    // Remove duplicates (if item with same id already exists)
    const filtered = existingItems.filter(i => i.id !== item.id);
    
    // Add new item to front and keep only 5 most recent
    const updated = [itemWithTime, ...filtered].slice(0, 5);
    setRecentFn(updated);
  };

  // ============================================================================
  // EPIC GENERATION & MANAGEMENT
  // ============================================================================
  // Generate Epics
  const handleGenerateEpics = async () => {
    if (!uploadId) {
      showMessage("error", "Please select an upload");
      return;
    }
    try {
      setLoadingEpics(true);
      setEpicProgress(10);
      
      const res = await generateEpicsAgent(parseInt(uploadId));
      setEpicProgress(50);
      
      const epics = res.data.data?.epics || [];
      setGeneratedEpics(epics);
      setEpicProgress(75);
      
      showMessage("success", "Epics generated successfully!");
      
      // Auto-create epics in Jira if credentials are configured
      if (jiraCredentials) {
        await createEpicsInJira(epics, uploadId);
      } else {
        // Mark all epics as failed if Jira credentials are not configured
        showMessage("warning", "⚠️ Jira credentials not configured. Epics marked as failed. Set up Jira integration to create epics.");
        // Mark all epics with failed status in the UI
        const token = localStorage.getItem("token");
        for (const epic of epics) {
          try {
            // Update backend to mark epic as failed
            await fetch(`${API_BASE_URL}/api/jira/mark-epic-failed`, {
              method: "POST",
              headers: {
                Authorization: `Bearer ${token}`,
                "Content-Type": "application/json",
              },
              body: JSON.stringify({
                epic_id: epic.id,
              }),
            });
          } catch (err) {
            console.error(`Failed to mark epic ${epic.id} as failed:`, err);
          }
        }
      }
      
      // Refresh the epics list
      await fetchEpics(uploadId, false);
    } catch (e) {
      showMessage("error", e.response?.data?.detail?.error || e.response?.data?.detail || "Failed to generate epics");
    } finally {
      setLoadingEpics(false);
      setEpicProgress(0);
    }
  };

  // Create all epics in Jira
  const createEpicsInJira = async (epics, uploadId) => {
    const token = localStorage.getItem("token");
    let successCount = 0;
    let failureCount = 0;

    for (const epic of epics) {
      try {
        setLoadingJiraItems(prev => new Set([...prev, `epic_${epic.id}`]));
        
        const technicalImpl = epic.technicalImplementation || epic.content?.technicalImplementation || null;
        console.log(`Creating epic ${epic.name}:`, { technicalImplementation: technicalImpl, epicContent: epic.content });
        
        const response = await fetch(`${API_BASE_URL}/api/jira/create-epic`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            jira_url: jiraCredentials.jira_url,
            jira_username: jiraCredentials.jira_username,
            jira_api_token: jiraCredentials.jira_api_token,
            jira_project_key: jiraCredentials.jira_project_key,
            epic_name: epic.name || "Untitled Epic",
            epic_description: epic.description || epic.content?.description || "",
            epic_id: epic.id,
            technical_implementation: epic.technicalImplementation || epic.content?.technicalImplementation || null,
          }),
        });

        const data = await response.json();

        if (response.ok) {
          successCount++;
          setJiraResults(prev => ({
            ...prev,
            [`epic_${epic.id}`]: { key: data.key, url: data.url }
          }));
        } else {
          failureCount++;
          console.error(`Failed to create epic ${epic.name}:`, data);
        }
      } catch (err) {
        failureCount++;
        console.error(`Failed to create epic ${epic.name}:`, err);
      } finally {
        setLoadingJiraItems(prev => {
          const newSet = new Set(prev);
          newSet.delete(`epic_${epic.id}`);
          return newSet;
        });
      }
    }

    // Show summary message
    if (successCount > 0) {
      showMessage("success", `${successCount} epic(s) created in Jira`);
    }
    if (failureCount > 0) {
      showMessage("warning", `${failureCount} epic(s) failed to create in Jira`);
    }

    // Refresh epics to get persisted Jira data
    await fetchEpics(uploadId, false);
  };

  // ============================================================================
  // EPIC MANAGEMENT - Jira Retry & Creation
  // ============================================================================
  // Retry creating a single epic in Jira
  const retryCreateEpicInJira = async (epic) => {
    console.log("Retry button clicked for epic:", epic.id, epic.name);
    
    // Check for Jira credentials
    const savedJiraCredentials = localStorage.getItem("jira_credentials");
    if (!savedJiraCredentials) {
      console.error("No Jira credentials found");
      const errorMsg = "Jira credentials not configured. Please configure Jira integration first.";
      showMessage("error", errorMsg);
      return;
    }

    let credentials;
    try {
      credentials = JSON.parse(savedJiraCredentials);
      console.log("Parsed Jira credentials");
    } catch (e) {
      console.error("Failed to parse credentials:", e);
      const errorMsg = "Invalid Jira credentials. Please reconfigure Jira integration.";
      showMessage("error", errorMsg);
      return;
    }

    const token = localStorage.getItem("token");
    if (!token) {
      const errorMsg = "Not authenticated. Please login first.";
      showMessage("error", errorMsg);
      return;
    }

    try {
      console.log("Setting loading state for epic:", epic.id);
      setLoadingJiraItems(prev => new Set([...prev, `epic_${epic.id}`]));
      
      const technicalImpl = epic.technicalImplementation || epic.content?.technicalImplementation || null;
      console.log(`Retrying epic creation for ${epic.name}:`, { technicalImplementation: technicalImpl, epicContent: epic.content });
      
      console.log("Making API call to create-epic");
      const response = await fetch(`${API_BASE_URL}/api/jira/create-epic`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          jira_url: credentials.jira_url,
          jira_username: credentials.jira_username,
          jira_api_token: credentials.jira_api_token,
          jira_project_key: credentials.jira_project_key,
          epic_name: epic.name || "Untitled Epic",
          epic_description: epic.description || epic.content?.description || "",
          epic_id: epic.id,
          technical_implementation: epic.technicalImplementation || epic.content?.technicalImplementation || null,
        }),
      });

      const data = await response.json();
      console.log("API Response:", response.status, data);

      if (response.ok) {
        console.log("Epic created successfully");
        setJiraResults(prev => ({
          ...prev,
          [`epic_${epic.id}`]: { key: data.key, url: data.url }
        }));
        const successMsg = `Epic "${epic.name}" created in Jira successfully!`;
        showMessage("success", successMsg);
        console.log(successMsg);
        
        // Refresh epics to get persisted Jira data
        const uploadId = Number.parseInt(localStorage.getItem("lastSelectedUploadId")) || generatedEpics[0]?.upload_id;
        if (uploadId) {
          console.log("Refreshing epics for upload:", uploadId);
          await fetchEpics(uploadId, false);
        }
      } else {
        console.error(`Failed to create epic ${epic.name}:`, data);
        const errorMsg = `Failed to create epic: ${data.detail || data.errors?.description || "Unknown error"}`;
        showMessage("error", errorMsg);
      }
    } catch (err) {
      console.error(`Failed to retry epic creation for ${epic.name}:`, err);
      const errorMsg = `Error: ${err.message || "Failed to create epic. Please try again."}`;
      showMessage("error", errorMsg);
    } finally {
      console.log("Clearing loading state for epic:", epic.id);
      setLoadingJiraItems(prev => {
        const newSet = new Set(prev);
        newSet.delete(`epic_${epic.id}`);
        return newSet;
      });
    }
  };

  // ============================================================================
  // STORY MANAGEMENT - Jira Retry & Creation
  // ============================================================================
  // Retry creating a single story in Jira
  const retryCreateStoryInJira = async (story) => {
    console.log("Retry button clicked for story:", story.id, story.name);
    console.log("Story object:", story);
    
    // Check for Jira credentials
    const savedJiraCredentials = localStorage.getItem("jira_credentials");
    if (!savedJiraCredentials) {
      console.error("No Jira credentials found");
      const errorMsg = "Jira credentials not configured. Please configure Jira integration first.";
      showMessage("error", errorMsg);
      return;
    }

    let credentials;
    try {
      credentials = JSON.parse(savedJiraCredentials);
      console.log("Parsed Jira credentials");
    } catch (e) {
      console.error("Failed to parse credentials:", e);
      const errorMsg = "Invalid Jira credentials. Please reconfigure Jira integration.";
      showMessage("error", errorMsg);
      return;
    }

    const token = localStorage.getItem("token");
    if (!token) {
      const errorMsg = "Not authenticated. Please login first.";
      showMessage("error", errorMsg);
      return;
    }

    try {
      console.log("Setting loading state for story:", story.id);
      setLoadingJiraItems(prev => new Set([...prev, `story_${story.id}`]));
      
      const acceptanceCriteria = story.acceptanceCriteria || story.content?.acceptanceCriteria || [];
      console.log(`Retrying story creation for ${story.name}:`, { acceptanceCriteria, storyContent: story.content });
      
      // Get epic_id - it might be stored directly or in the story object
      const epicId = story.epic_id || Number.parseInt(epicIdForStories);
      console.log("Epic ID for story:", epicId);
      
      // Find the parent epic for this story
      const parentEpic = generatedEpics.find(e => e.id === epicId);
      console.log("Parent epic found:", parentEpic);
      
      if (!parentEpic) {
        const errorMsg = "Parent epic not found. Please refresh the page and try again.";
        showMessage("error", errorMsg);
        return;
      }
      
      if (!parentEpic.jira_issue_id) {
        const errorMsg = "Parent epic not created in Jira. Please create the epic first.";
        showMessage("error", errorMsg);
        return;
      }
      
      console.log("Making API call to create-story-jira with:", {
        epic_jira_issue_id: parentEpic.jira_issue_id,
        epic_jira_key: parentEpic.jira_key,
        final_story_name: story.name,
        story_description: story.description || story.content?.description,
      });
      
      const response = await fetch(`${API_BASE_URL}/api/jira/create-story-jira`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          jira_url: credentials.jira_url,
          jira_username: credentials.jira_username,
          jira_api_token: credentials.jira_api_token,
          jira_project_key: credentials.jira_project_key,
          epic_jira_issue_id: parentEpic.jira_issue_id,
          epic_jira_key: parentEpic.jira_key,
          final_story_name: story.name || "Untitled Story",
          story_description: story.description || story.content?.description || "",
          story_acceptance_criteria: acceptanceCriteria.join("\n") || "",
          story_id: story.id,
        }),
      });

      const data = await response.json();
      console.log("API Response:", response.status, data);

      if (response.ok) {
        console.log("Story created successfully");
        setJiraResults(prev => ({
          ...prev,
          [`story_${story.id}`]: { key: data.key, url: data.url }
        }));
        const successMsg = `Story "${story.name}" created in Jira successfully!`;
        showMessage("success", successMsg);
        console.log(successMsg);
        
        // Refresh stories to get persisted Jira data
        const epicId = story.epic_id || Number.parseInt(epicIdForStories);
        if (epicId) {
          console.log("Refreshing stories for epic:", epicId);
          await fetchStories(epicId);
        }
      } else {
        console.error(`Failed to create story ${story.name}:`, data);
        const errorMsg = `Failed to create story: ${data.detail || data.errors?.description || "Unknown error"}`;
        showMessage("error", errorMsg);
      }
    } catch (err) {
      console.error(`Failed to retry story creation for ${story.name}:`, err);
      const errorMsg = `Error: ${err.message || "Failed to create story. Please try again."}`;
      showMessage("error", errorMsg);
    } finally {
      console.log("Clearing loading state for story:", story.id);
      setLoadingJiraItems(prev => {
        const newSet = new Set(prev);
        newSet.delete(`story_${story.id}`);
        return newSet;
      });
    }
  };

  // Create all stories in Jira as subtasks under epic
  const createStoriesInJira = async (stories, epicId, epic) => {
    const token = localStorage.getItem("token");
    let successCount = 0;
    let failureCount = 0;

    for (const story of stories) {
      try {
        setLoadingJiraItems(prev => new Set([...prev, `story_${story.id}`]));
        
        const response = await fetch(`${API_BASE_URL}/api/jira/create-story-jira`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            jira_url: jiraCredentials.jira_url,
            jira_username: jiraCredentials.jira_username,
            jira_api_token: jiraCredentials.jira_api_token,
            jira_project_key: jiraCredentials.jira_project_key,
            epic_jira_issue_id: epic.jira_issue_id,
            epic_jira_key: epic.jira_key,
            final_story_name: story.name || "Untitled Story",
            story_description: story.description || story.content?.description || "",
            story_id: story.id,
          }),
        });

        const data = await response.json();

        if (response.ok) {
          successCount++;
          setJiraResults(prev => ({
            ...prev,
            [`story_${story.id}`]: { key: data.key, url: data.url }
          }));
        } else {
          failureCount++;
        }
      } catch (err) {
        failureCount++;
        console.error(`Failed to create story ${story.name}:`, err);
      } finally {
        setLoadingJiraItems(prev => {
          const newSet = new Set(prev);
          newSet.delete(`story_${story.id}`);
          return newSet;
        });
      }
    }

    // Show summary message
    if (successCount > 0) {
      showMessage("success", `${successCount} story/stories created as subtasks in Jira`);
    }
    if (failureCount > 0) {
      showMessage("warning", `${failureCount} story/stories failed to create in Jira`);
    }

    // Refresh stories to get persisted Jira data
    await fetchStories(epicId, false);
  };

  // Create Epic in Jira
  const handleCreateEpicInJira = async (epic) => {
    if (!jiraCredentials) {
      showMessage("error", "Jira credentials not configured. Please set up Jira integration first.");
      return;
    }

    const itemKey = `epic_${epic.id}`;
    try {
      setLoadingJiraItems(prev => new Set([...prev, itemKey]));
      const token = localStorage.getItem("token");
      const response = await fetch(`${API_BASE_URL}/api/jira/create-epic`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          jira_url: jiraCredentials.jira_url,
          jira_username: jiraCredentials.jira_username,
          jira_api_token: jiraCredentials.jira_api_token,
          jira_project_key: jiraCredentials.jira_project_key,
          epic_name: epic.name,
          epic_description: epic.description || epic.content?.description || "",
          epic_id: epic.id,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        showMessage("success", `Epic created in Jira: ${data.key}. View link in EPIC page.`);
        setJiraResults(prev => ({
          ...prev,
          [itemKey]: { key: data.key, url: data.url }
        }));
        // Refresh epics to get the persisted Jira data from backend
        if (uploadId) {
          await fetchEpics(uploadId, true);
        }
      } else {
        showMessage("error", "Failed to create epic in Jira. Please check your Jira credentials and try again.");
      }
    } catch (err) {
      showMessage("error", "Unable to create epic. Please check your connection and try again.");
    } finally {
      setLoadingJiraItems(prev => {
        const newSet = new Set(prev);
        newSet.delete(itemKey);
        return newSet;
      });
    }
  };

  // Fetch epics for selected upload
  const fetchEpics = async (uId, shouldMerge = true) => {
    if (!uId) return;
    try {
      const res = await getEpicsAgent(parseInt(uId));
      const epics = res.data.data?.epics || [];
      
      if (shouldMerge) {
        // Merge with existing epics to preserve Jira links (avoid duplicates by ID)
        setGeneratedEpics(prevEpics => {
          const existingMap = new Map(prevEpics.map(e => [e.id, e]));
          epics.forEach(epic => {
            existingMap.set(epic.id, epic); // Update with latest data
          });
          return Array.from(existingMap.values());
        });
      } else {
        // Replace completely (fresh load)
        setGeneratedEpics(epics);
      }
      
      // Add each epic to recent list
      epics.forEach(epic => {
        addToRecent(setRecentEpics, epic, recentEpics);
      });
    } catch (error) {
      console.error("Failed to fetch epics:", error);
      const errorMsg = error.response?.data?.detail?.error || error.response?.data?.detail || error.message || "Failed to fetch epics";
      console.error("Detailed error:", errorMsg);
    }
  };

  // Auto-fetch epics when uploadId changes
  useEffect(() => {
    if (uploadId) {
      fetchEpics(uploadId);
    }
  }, [uploadId]);

  // Handle upload selection
  const handleUploadChange = (e) => {
    const uId = e.target.value;
    setUploadId(uId);
    
    // Add to recent uploads list
    if (uId) {
      const selectedUpload = userUploads.find(u => u.id === parseInt(uId));
      if (selectedUpload) {
        const itemWithTime = { ...selectedUpload, timestamp: Date.now() };
        const filtered = recentUploads.filter(item => item.id !== selectedUpload.id);
        const updated = [itemWithTime, ...filtered].slice(0, 5);
        setRecentUploads(updated);
      }
      localStorage.setItem("lastSelectedUploadId", uId);
    } else {
      localStorage.removeItem("lastSelectedUploadId");
    }
    // Clear generated content when upload changes
    setGeneratedEpics([]);
    setEpicIdForStories("");
    setEpicIdForTestPlan("");
    setGeneratedStories([]);
    setGeneratedTestPlans([]);
    setStoryId("");
    setGeneratedQA([]);
    // fetchEpics will be called automatically via useEffect
  };

  // ============================================================================
  // STORY GENERATION & MANAGEMENT
  // ============================================================================
  // Create Story in Jira
  const handleCreateStoryInJira = async (story, epicId) => {
    if (!jiraCredentials) {
      showMessage("error", "Jira credentials not configured. Please set up Jira integration first.");
      return;
    }

    // Get the epic's Jira information from generatedEpics
    const epic = generatedEpics.find(e => e.id === Number(epicId));
    const epicJiraKey = epic?.jira_key;
    const epicJiraIssueId = epic?.jira_issue_id;

    if (!epicJiraIssueId) {
      showMessage("error", "Epic Jira issue ID not available. Please ensure the epic is created in Jira first.");
      return;
    }

    const itemKey = `story_${story.id}`;
    try {
      setLoadingJiraItems(prev => new Set([...prev, itemKey]));
      const token = localStorage.getItem("token");
      const response = await fetch(`${API_BASE_URL}/api/jira/create-story-jira`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          jira_url: jiraCredentials.jira_url,
          jira_username: jiraCredentials.jira_username,
          jira_api_token: jiraCredentials.jira_api_token,
          jira_project_key: jiraCredentials.jira_project_key,
          story_title: story.title || story.name,
          story_description: story.description || story.content?.description || "",
          story_acceptance_criteria: story.acceptance_criteria || "",
          epic_id: epicId,
          story_id: story.id,
          epic_jira_key: epicJiraKey,
          epic_jira_issue_id: epicJiraIssueId,  // Pass epic's numeric Jira issue ID for parent field
        }),
      });

      const data = await response.json();

      if (response.ok) {
        showMessage("success", `Story created in Jira: ${data.key}. View link in STORY page.`);
        setJiraResults(prev => ({
          ...prev,
          [itemKey]: { key: data.key, url: data.url }
        }));
        // Refresh stories to get the persisted Jira data from backend
        if (epicIdForStories) {
          await fetchStories(epicIdForStories, true);
        }
      } else {
        showMessage("error", "Failed to create story in Jira. Please check your Jira credentials and try again.");
      }
    } catch (err) {
      showMessage("error", "Unable to create story. Please check your connection and try again.");
    } finally {
      setLoadingJiraItems(prev => {
        const newSet = new Set(prev);
        newSet.delete(itemKey);
        return newSet;
      });
    }
  };

  // Generate Stories
  const handleGenerateStories = async () => {
    if (!epicIdForStories) {
      showMessage("error", "Please select an epic");
      return;
    }
    try {
      setLoadingStories(true);
      setStoryProgress(10);
      
      const res = await generateStoriesAgent(Number.parseInt(epicIdForStories));
      setStoryProgress(50);
      
      const stories = res.data.data?.stories || [];
      setGeneratedStories(stories);
      setStoryProgress(75);
      
      showMessage("success", "Stories generated successfully!");
      
      // Auto-create stories in Jira if credentials are configured
      if (jiraCredentials) {
        // Get the epic to pass Jira issue ID for parent linking
        const epic = generatedEpics.find(e => e.id === Number.parseInt(epicIdForStories));
        if (epic && epic.jira_issue_id) {
          await createStoriesInJira(stories, epicIdForStories, epic);
        } else {
          showMessage("warning", "Parent epic not created in Jira. Stories marked as failed. Set up the epic in Jira first to link stories.");
          // Mark all stories as failed
          const token = localStorage.getItem("token");
          for (const story of stories) {
            try {
              await fetch(`${API_BASE_URL}/api/jira/mark-story-failed`, {
                method: "POST",
                headers: {
                  Authorization: `Bearer ${token}`,
                  "Content-Type": "application/json",
                },
                body: JSON.stringify({
                  story_id: story.id,
                }),
              });
            } catch (err) {
              console.error(`Failed to mark story ${story.id} as failed:`, err);
            }
          }
        }
      } else {
        showMessage("warning", "Jira credentials not configured. Stories marked as failed. Set up Jira integration to create stories.");
        // Mark all stories as failed
        const token = localStorage.getItem("token");
        for (const story of stories) {
          try {
            await fetch(`${API_BASE_URL}/api/jira/mark-story-failed`, {
              method: "POST",
              headers: {
                Authorization: `Bearer ${token}`,
                "Content-Type": "application/json",
              },
              body: JSON.stringify({
                story_id: story.id,
              }),
            });
          } catch (err) {
            console.error(`Failed to mark story ${story.id} as failed:`, err);
          }
        }
      }
      
      // Refresh the stories list
      await fetchStories(epicIdForStories, false);
    } catch (e) {
      showMessage("error", e.response?.data?.detail?.error || e.response?.data?.detail || "Failed to generate stories");
    } finally {
      setLoadingStories(false);
      setStoryProgress(0);
    }
  };

  // ============================================================================
  // STORY FETCHING & AUTO-LOADING
  // ============================================================================
  // Fetch stories for selected epic
  const fetchStories = async (epicId, shouldMerge = true) => {
    if (!epicId) return;
    console.log("Fetching stories for epic:", epicId);
    try {
      const res = await getStoriesAgent(parseInt(epicId));
      console.log("Stories response:", res.data);
      const stories = res.data.data?.stories || [];
      console.log("Stories to display:", stories);
      
      if (shouldMerge) {
        // Merge with existing stories to preserve Jira links (avoid duplicates by ID)
        setGeneratedStories(prevStories => {
          const existingMap = new Map(prevStories.map(s => [s.id, s]));
          stories.forEach(story => {
            existingMap.set(story.id, story); // Update with latest data
          });
          return Array.from(existingMap.values());
        });
      } else {
        // Replace: fresh load from dropdown selection
        setGeneratedStories(stories);
      }
      
      // Add each story to recent list
      stories.forEach(story => {
        addToRecent(setRecentStories, story, recentStories);
      });
      if (stories.length === 0) {
        console.warn("No stories returned for epic", epicId);
      }
    } catch (error) {
      console.error("Failed to fetch stories:", error);
      const errorMsg = error.response?.data?.detail?.error || error.response?.data?.detail || error.message || "Failed to fetch stories";
      console.error("Detailed error:", errorMsg);
      showMessage("error", `Could not load stories: ${errorMsg}`);
    }
  };

  // ============================================================================
  // STORY FETCHING & AUTO-LOADING
  // ============================================================================
  // Auto-fetch stories when epicIdForStories changes
  useEffect(() => {
    if (epicIdForStories) {
      fetchStories(epicIdForStories);
    }
  }, [epicIdForStories]);

  // Handle epic selection for stories
  const handleEpicForStoriesChange = (e) => {
    const epicId = e.target.value;
    console.log("Epic selected for stories:", epicId);
    setEpicIdForStories(epicId);
    // Save to localStorage for restoration on component remount
    if (epicId) {
      localStorage.setItem("lastSelectedEpicForStories", epicId);
    } else {
      localStorage.removeItem("lastSelectedEpicForStories");
    }
    setStoryId("");
    setGeneratedStories([]);
    setGeneratedQA([]);
    // fetchStories will be called automatically via useEffect
  };

  // Generate QA
  const handleGenerateQA = async () => {
    if (!storyId) {
      showMessage("error", "Please select a story");
      return;
    }

    // Check if regeneration limit reached
    const currentAttempts = qaRegenerationAttempts[storyId] || 0;
    if (currentAttempts >= 3) {
      showMessage("error", "Maximum regeneration attempts (3) reached for this story. Please select a different story.");
      return;
    }

    try {
      setLoadingQA(true);
      setQAProgress(10);
      
      const res = await generateQAAgent(parseInt(storyId));
      setQAProgress(50);
      
      console.log("Generate QA response:", res.data);
      const qa = res.data.data?.qa_tests || res.data.data?.qa || [];
      console.log("QA tests from generate response:", qa);
      
      if (qa && qa.length > 0) {
        setGeneratedQA(qa);
        console.log("Set generatedQA to:", qa);
      } else {
        console.warn("No QA tests in response");
      }
      
      setQAProgress(75);
      
      // Increment regeneration attempt counter
      setQaRegenerationAttempts(prev => ({
        ...prev,
        [storyId]: (prev[storyId] || 0) + 1
      }));
      
      showMessage("success", "QA tests generated successfully!");
      // Refresh the QA list
      await fetchQA(storyId);
    } catch (e) {
      console.error("Generate QA error:", e);
      showMessage("error", e.response?.data?.detail?.error || e.response?.data?.detail || "Failed to generate QA tests");
    } finally {
      setLoadingQA(false);
      setQAProgress(0);
    }
  };

  // Fetch QA for selected story
  const fetchQA = async (sId) => {
    if (!sId) return;
    console.log("Fetching QA for story:", sId);
    try {
      const res = await getQAAgent(parseInt(sId));
      console.log("QA full response:", res.data);
      
      // Extract qa_tests from the response - handle different response structures
      let qa = [];
      if (res.data?.data?.qa_tests) {
        qa = res.data.data.qa_tests;
      } else if (res.data?.qa_tests) {
        qa = res.data.qa_tests;
      } else if (Array.isArray(res.data?.data)) {
        qa = res.data.data;
      } else if (Array.isArray(res.data)) {
        qa = res.data;
      }
      
      console.log("Extracted QA tests:", qa);
      
      if (!Array.isArray(qa)) {
        console.error("QA tests is not an array:", qa);
        qa = [];
      }
      
      // Merge with existing QA to preserve data (avoid duplicates by ID)
      setGeneratedQA(prevQA => {
        console.log("Previous QA:", prevQA);
        const existingMap = new Map(prevQA.map(q => [q.id, q]));
        qa.forEach(qaItem => {
          existingMap.set(qaItem.id, qaItem); // Update with latest data
        });
        const merged = Array.from(existingMap.values());
        console.log("Merged QA:", merged);
        return merged;
      });
      
      // Add each QA to recent list
      qa.forEach(qaItem => {
        addToRecent(setRecentQA, qaItem, recentQA);
      });
      
      if (qa.length === 0) {
        console.warn("No QA tests returned for story", sId);
      }
    } catch (error) {
      console.error("Failed to fetch QA:", error);
      const errorMsg = error.response?.data?.detail?.error || error.response?.data?.detail || error.message || "Failed to fetch QA";
      console.error("Detailed error:", errorMsg);
      // Don't show error message for 404, it's expected when no QA tests exist yet
      if (error.response?.status !== 404) {
        showMessage("error", `Could not load QA tests: ${errorMsg}`);
      }
    }
  };

  // Auto-fetch QA when storyId changes
  useEffect(() => {
    if (storyId) {
      fetchQA(storyId);
    }
  }, [storyId]);

  // Handle story selection
  const handleStoryChange = (e) => {
    const sId = e.target.value;
    console.log("Story selected for QA:", sId);
    setStoryId(sId);
    // Save to localStorage for restoration on component remount
    if (sId) {
      localStorage.setItem("lastSelectedStoryId", sId);
    } else {
      localStorage.removeItem("lastSelectedStoryId");
    }
    setGeneratedQA([]);
    // Reset regeneration attempts for new story
    if (sId) {
      setQaRegenerationAttempts(prev => ({
        ...prev,
        [sId]: 0
      }));
    }
    // fetchQA will be called automatically via useEffect
  };

  // Generate Test Plan
  const handleGenerateTestPlan = async () => {
    if (!epicIdForTestPlan) {
      showMessage("error", "Please select an epic");
      return;
    }
    try {
      setLoadingTestPlan(true);
      setTestPlanProgress(10);
      
      const res = await generateTestPlanAgent(parseInt(epicIdForTestPlan));
      setTestPlanProgress(50);
      
      const testPlans = res.data.data?.test_plans || res.data.test_plans || [];
      setGeneratedTestPlans(testPlans);
      setTestPlanProgress(75);
      
      showMessage("success", "Test plan generated successfully!");
      // Refresh the test plans list
      await fetchTestPlans(epicIdForTestPlan);
    } catch (e) {
      showMessage("error", e.response?.data?.detail?.error || e.response?.data?.detail || "Failed to generate test plan");
    } finally {
      setLoadingTestPlan(false);
      setTestPlanProgress(0);
    }
  };

  // Fetch test plans for selected epic
  const fetchTestPlans = async (epicId) => {
    if (!epicId) return;
    console.log("Fetching test plans for epic:", epicId);
    try {
      const res = await getTestPlanAgent(parseInt(epicId));
      console.log("Test plans response:", res.data);
      const testPlans = res.data.data?.test_plans || [];
      console.log("Test plans to display:", testPlans);
      // Merge with existing test plans to preserve data (avoid duplicates by ID)
      setGeneratedTestPlans(prevPlans => {
        const existingMap = new Map(prevPlans.map(p => [p.id, p]));
        testPlans.forEach(plan => {
          existingMap.set(plan.id, plan); // Update with latest data
        });
        return Array.from(existingMap.values());
      });
      if (testPlans.length === 0) {
        console.warn("No test plans returned for epic", epicId);
      }
    } catch (error) {
      console.error("Failed to fetch test plans:", error);
      const errorMsg = error.response?.data?.detail?.error || error.response?.data?.detail || error.message || "Failed to fetch test plans";
      console.error("Detailed error:", errorMsg);
      showMessage("error", `Could not load test plans: ${errorMsg}`);
    }
  };

  // Auto-fetch test plans when epicIdForTestPlan changes
  useEffect(() => {
    if (epicIdForTestPlan) {
      fetchTestPlans(epicIdForTestPlan);
    }
  }, [epicIdForTestPlan]);

  // Handle epic selection for test plan
  const handleEpicForTestPlanChange = (e) => {
    const epicId = e.target.value;
    console.log("Epic selected for test plan:", epicId);
    setEpicIdForTestPlan(epicId);
    // Save to localStorage for restoration on component remount
    if (epicId) {
      localStorage.setItem("lastSelectedEpicForTestPlan", epicId);
    } else {
      localStorage.removeItem("lastSelectedEpicForTestPlan");
    }
    setGeneratedTestPlans([]);
    // fetchTestPlans will be called automatically via useEffect
  };

  // RAG Search
  const handleRAGSearch = async () => {
    if (!ragQuery) {
      showMessage("error", "Please enter a search query");
      return;
    }
    try {
      setLoadingRAG(true);
      const res = await ragVectorStoreSearch(ragQuery, 5);
      setRagResults(res.data.search_results || []);
      showMessage("success", `Found ${(res.data.search_results || []).length} documents!`);
    } catch (e) {
      showMessage("error", e.response?.data?.detail || "Failed to search documents");
    } finally {
      setLoadingRAG(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-6 md:p-10">
      {/* Toast Notifications */}
      <Toast 
        ref={toast} 
        position="top-center"
        itemTemplate={(item) => (
          <div className="flex items-center gap-4 w-full px-4 py-3">
            <div className="flex-shrink-0 text-xl">
              {item.severity === "success" && <FaCheckCircle />}
              {item.severity === "error" && <FaTimesCircle />}
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-bold text-base">{item.summary}</p>
              <p className="text-sm opacity-90">{item.detail}</p>
            </div>
          </div>
        )}
      />

      {/* Header */}
      <div className="mb-20 px-8 py-12 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-gray-800 dark:to-gray-700 rounded-3xl border border-blue-100 dark:border-gray-600 shadow-xl">
        <div className="flex items-center gap-8">
          <div className="p-5 bg-blue-100 dark:bg-blue-900 rounded-xl flex-shrink-0 shadow-md">
            <FaRobot className="text-5xl text-blue-600 dark:text-blue-300" />
          </div>
          <div className="flex-1">
            <h1 className="text-6xl font-bold text-gray-900 dark:text-white mb-4">Requirment Analyser Agents</h1>
            <p className="text-gray-600 dark:text-gray-300 text-lg leading-relaxed font-medium">
              Use specialized agents to generate epics, stories, and QA tests from your requirements
            </p>
          </div>
        </div>
      </div>

      {/* Accordion for Agent Sections */}
      <div className="mb-10 px-4">
        <p className="text-lg font-semibold text-gray-700 dark:text-gray-300">Select a section below to expand and manage your agents</p>
      </div>
      <style>{`
        .p-accordion .p-accordion-header .p-accordion-toggle-icon {
          font-weight: bold;
          margin-right: 0.75rem;
        }
        .p-accordion .p-accordion-header {
          padding-left: 1.5rem !important;
        }
      `}</style>
      <Accordion className="mb-20" activeIndex={0}>
        {/* Generate Epics Tab */}
        <AccordionTab header="Generate Epics" headerClassName="bg-purple-100 dark:bg-purple-900 text-purple-900 dark:text-purple-100 font-bold py-6 text-xl border-2 border-purple-300 dark:border-purple-700 rounded-lg transition hover:bg-purple-200 dark:hover:bg-purple-800 hover:shadow-md mb-6">
          <div className="space-y-10 pt-8 pb-8">
            <div className="space-y-4">
              <label className="block text-lg font-bold text-gray-800 dark:text-gray-200 mb-5">
                <span>Select Upload</span> {userUploads.length > 0 && <span className="text-purple-600 ml-2">({userUploads.length})</span>}
              </label>
              {loadingUploads ? (
                <div className="flex items-center justify-center py-6">
                  <FaSpinner className="animate-spin text-purple-500 text-2xl" />
                </div>
              ) : (
                <Dropdown
                  value={uploadId}
                  onChange={(e) => handleUploadChange({ target: { value: e.value } })}
                  options={[
                    recentUploads.length > 0 ? {
                      label: "📌 Recent Uploads",
                      items: recentUploads.map((upload) => ({
                        label: `⭐ ${upload.filename} (ID: ${upload.id})`,
                        value: upload.id
                      }))
                    } : null,
                    userUploads.length > 0 ? {
                      label: "All Uploads",
                      items: userUploads.map((upload) => ({
                        label: `${upload.filename} (ID: ${upload.id})`,
                        value: upload.id
                      }))
                    } : null
                  ].filter(Boolean)}
                  optionGroupLabel="label"
                  optionGroupChildren="items"
                  placeholder="-- Choose an upload --"
                  className="w-full text-base"
                  panelClassName="dark:bg-gray-700 dark:text-white max-h-96 overflow-y-auto"
                  showClear
                />
              )}
            </div>
            <div className="relative group mt-6">
              <Button
                onClick={handleGenerateEpics}
                disabled={loadingEpics || !uploadId || generatedEpics.length > 0}
                severity="success"
                className="w-full py-4 text-base font-semibold"
                style={{ backgroundColor: '#a855f7', borderColor: '#a855f7' }}
                icon={loadingEpics ? undefined : "pi pi-arrow-right"}
                loading={loadingEpics}
                label={loadingEpics ? `Generating... ${epicProgress}%` : "Generate Epics"}
              />
              {epicProgress > 0 && loadingEpics && (
                <div className="mt-4 w-full bg-gray-300 dark:bg-gray-600 rounded-full h-3">
                  <div 
                    className="bg-purple-500 h-3 rounded-full transition-all duration-300"
                    style={{ width: `${epicProgress}%` }}
                  />
                </div>
              )}
              {generatedEpics.length > 0 && (
                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-800 text-white text-sm rounded opacity-0 group-hover:opacity-100 transition whitespace-nowrap pointer-events-none z-10">
                  Epics already present
                </div>
              )}
            </div>

            {generatedEpics.length > 0 && (
              <div className="pt-10 mt-10 border-t-2 border-gray-300 dark:border-gray-600">
                <h3 className="font-bold text-2xl text-gray-900 dark:text-white mb-8 flex items-center gap-4">
                  <span className="w-2 h-8 bg-purple-500 rounded-full"></span>
                  Generated Epics ({generatedEpics.length})
                </h3>
                <DataTable
                  value={generatedEpics}
                  emptyMessage="No epics generated"
                  className="p-datatable-striped p-datatable-sm"
                  responsiveLayout="scroll"
                  stripedRows
                  dataKey="id"
                  scrollable
                  scrollHeight="400px"
                  style={{ borderRadius: '0.5rem' }}
                >
                  <Column
                    field="id"
                    header="ID"
                    style={{ width: '80px' }}
                    bodyClassName="text-gray-900 dark:text-gray-100 font-medium"
                  />
                  <Column
                    field="name"
                    header="Epic Name"
                    style={{ width: '250px' }}
                    bodyClassName="text-gray-900 dark:text-gray-100"
                  />
                  <Column
                    header="Confluence"
                    style={{ width: '130px' }}
                    body={(rowData) => (
                      rowData.confluence_page_url ? (
                        <Button
                          onClick={() => window.open(rowData.confluence_page_url, '_blank')}
                          label="View"
                          icon="pi pi-external-link"
                          className="p-button-sm p-button-rounded"
                          style={{ backgroundColor: '#a855f7', borderColor: '#a855f7' }}
                          title="View on Confluence"
                        />
                      ) : (
                        <span className="text-gray-400 text-sm">N/A</span>
                      )
                    )}
                  />
                  <Column
                    header="Jira Link"
                    style={{ width: '130px' }}
                    body={(rowData) => (
                      rowData.jira_url ? (
                        <Button
                          onClick={() => window.open(rowData.jira_url, '_blank')}
                          label={rowData.jira_key || 'Open'}
                          icon="pi pi-external-link"
                          className="p-button-sm p-button-rounded"
                          style={{ backgroundColor: '#3b82f6', borderColor: '#3b82f6' }}
                          title="View on Jira"
                        />
                      ) : (
                        <span className="text-gray-400 text-sm">N/A</span>
                      )
                    )}
                  />
                  <Column
                    header="Jira Status"
                    style={{ width: '140px' }}
                    body={(rowData) => {
                      const isLoading = loadingJiraItems.has(`epic_${rowData.id}`);
                      const creationSuccess = rowData.jira_creation_success;
                      
                      if (isLoading) {
                        return (
                          <div className="inline-flex items-center gap-1 px-2 py-1 bg-gray-400 text-white rounded text-xs whitespace-nowrap">
                            <FaSpinner className="animate-spin" />
                            Creating...
                          </div>
                        );
                      }

                      if (creationSuccess === true) {
                        return (
                          <div className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 rounded text-xs whitespace-nowrap" title="Jira creation successful">
                            <FaCheckCircle /> Success
                          </div>
                        );
                      }

                      if (creationSuccess === false) {
                        return (
                          <div className="group relative inline-flex">
                            <button
                              onClick={() => retryCreateEpicInJira(rowData)}
                              type="button"
                              className="inline-flex items-center gap-1 px-2 py-1 bg-red-100 hover:bg-red-200 text-red-700 rounded text-xs whitespace-nowrap transition hover:cursor-pointer"
                              title="Click to retry creating this epic in Jira"
                            >
                              <FaTimesCircle /> Failed
                            </button>
                            <div className="invisible group-hover:visible absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-800 text-white rounded text-xs whitespace-nowrap z-10 pointer-events-none">
                              Click to retry
                              <div className="absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-gray-800"></div>
                            </div>
                          </div>
                        );
                      }

                      return (
                        <span className="text-gray-400 text-sm">N/A</span>
                      );
                    }}
                  />
                </DataTable>
              </div>
            )}
          </div>
        </AccordionTab>

        {/* Generate Stories Tab */}
        <AccordionTab header="Generate Stories" headerClassName="bg-green-100 dark:bg-green-900 text-green-900 dark:text-green-100 font-bold py-6 text-xl border-2 border-green-300 dark:border-green-700 rounded-lg transition hover:bg-green-200 dark:hover:bg-green-800 hover:shadow-md mb-6">
          <div className="space-y-10 pt-8 pb-8">
            <div>
              <label className="block text-lg font-bold text-gray-800 dark:text-gray-200 mb-5">
                <span>Select Epic</span> {generatedEpics.length > 0 && <span className="text-green-600 ml-2">({generatedEpics.length})</span>}
              </label>
              <Dropdown
                value={epicIdForStories}
                onChange={(e) => handleEpicForStoriesChange({ target: { value: e.value } })}
                options={[
                  recentEpics.length > 0 ? {
                    label: "📌 Recent Epics",
                    items: recentEpics.map((epic) => ({
                      label: `⭐ ${epic.name} (ID: ${epic.id})`,
                      value: epic.id
                    }))
                  } : null,
                  generatedEpics.length > 0 ? {
                    label: "All Epics",
                    items: generatedEpics.map((epic) => ({
                      label: `${epic.name} (ID: ${epic.id})`,
                      value: epic.id
                    }))
                  } : null
                ].filter(Boolean)}
                optionGroupLabel="label"
                optionGroupChildren="items"
                placeholder="-- Choose an epic --"
                className="w-full text-base"
                panelClassName="dark:bg-gray-700 dark:text-white max-h-96 overflow-y-auto"
                showClear
              />
              {generatedEpics.length === 0 && uploadId && (
                <p className="text-base text-gray-600 dark:text-gray-400 mt-4">
                  💡 Select an upload first - epic list will load automatically
                </p>
              )}
              {!uploadId && (
                <p className="text-base text-amber-600 dark:text-amber-400 mt-4">
                  ⚠️ Select an upload from the first tab to load epics
                </p>
              )}
            </div>
            <div className="relative group mt-6">
              <Button
                onClick={handleGenerateStories}
                disabled={loadingStories || !epicIdForStories || generatedStories.length > 0}
                severity="success"
                className="w-full py-4 text-base font-semibold"
                style={{ backgroundColor: '#22c55e', borderColor: '#22c55e' }}
                icon={loadingStories ? undefined : "pi pi-arrow-right"}
                loading={loadingStories}
                label={loadingStories ? `Generating... ${storyProgress}%` : "Generate Stories"}
              />
              {storyProgress > 0 && loadingStories && (
                <div className="mt-4 w-full bg-gray-300 dark:bg-gray-600 rounded-full h-3">
                  <div 
                    className="bg-green-500 h-3 rounded-full transition-all duration-300"
                    style={{ width: `${storyProgress}%` }}
                  />
                </div>
              )}
              {generatedStories.length > 0 && (
                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-800 text-white text-sm rounded opacity-0 group-hover:opacity-100 transition whitespace-nowrap pointer-events-none z-10">
                  Stories already present
                </div>
              )}
            </div>
            {generatedStories.length === 0 && epicIdForStories && (
              <p className="text-base text-gray-600 dark:text-gray-400 mt-4">
                💡 No existing stories found. Generate stories from the selected epic.
              </p>
            )}
            {!epicIdForStories && generatedEpics.length > 0 && (
              <p className="text-base text-amber-600 dark:text-amber-400 mt-4">
                ⚠️ Select an epic from the dropdown to load stories
              </p>
            )}

            {generatedStories.length > 0 && (
              <div className="pt-10 mt-10 border-t-2 border-gray-300 dark:border-gray-600">
                <h3 className="font-bold text-2xl text-gray-900 dark:text-white mb-8 flex items-center gap-4">
                  <span className="w-2 h-8 bg-green-500 rounded-full"></span>
                  Generated Stories ({generatedStories.length})
                </h3>
                <DataTable
                  value={generatedStories}
                  emptyMessage="No stories generated"
                  className="p-datatable-striped p-datatable-sm"
                  responsiveLayout="scroll"
                  stripedRows
                  dataKey="id"
                  scrollable
                  scrollHeight="400px"
                  style={{ borderRadius: '0.5rem' }}
                >
                  <Column
                    field="id"
                    header="ID"
                    style={{ width: '80px' }}
                    bodyClassName="text-gray-900 dark:text-gray-100 font-medium"
                  />
                  <Column
                    field="name"
                    header="Story Name"
                    style={{ width: '250px' }}
                    body={(rowData) => rowData.name || "Untitled"}
                    bodyClassName="text-gray-900 dark:text-gray-100"
                  />
                  <Column
                    header="Jira Link"
                    style={{ width: '130px' }}
                    body={(rowData) => (
                      rowData.jira_url ? (
                        <Button
                          onClick={() => window.open(rowData.jira_url, '_blank')}
                          label={rowData.jira_key || 'Open'}
                          icon="pi pi-external-link"
                          className="p-button-sm p-button-rounded"
                          style={{ backgroundColor: '#3b82f6', borderColor: '#3b82f6' }}
                          title="View on Jira"
                        />
                      ) : (
                        <span className="text-gray-400 text-sm">N/A</span>
                      )
                    )}
                  />
                  <Column
                    header="Jira Status"
                    style={{ width: '140px' }}
                    body={(rowData) => {
                      const isLoading = loadingJiraItems.has(`story_${rowData.id}`);
                      const creationSuccess = rowData.jira_creation_success;
                      
                      if (isLoading) {
                        return (
                          <div className="inline-flex items-center gap-1 px-2 py-1 bg-gray-400 text-white rounded text-xs whitespace-nowrap">
                            <FaSpinner className="animate-spin" />
                            Creating...
                          </div>
                        );
                      }

                      if (creationSuccess === true) {
                        return (
                          <div className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 rounded text-xs whitespace-nowrap" title="Jira creation successful">
                            <FaCheckCircle /> Success
                          </div>
                        );
                      }

                      if (creationSuccess === false) {
                        return (
                          <div className="group relative inline-flex">
                            <button
                              onClick={() => retryCreateStoryInJira(rowData)}
                              type="button"
                              className="inline-flex items-center gap-1 px-2 py-1 bg-red-100 hover:bg-red-200 text-red-700 rounded text-xs whitespace-nowrap transition hover:cursor-pointer"
                              title="Click to retry creating this story in Jira"
                            >
                              <FaTimesCircle /> Failed
                            </button>
                            <div className="invisible group-hover:visible absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-800 text-white rounded text-xs whitespace-nowrap z-10 pointer-events-none">
                              Click to retry
                              <div className="absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-gray-800"></div>
                            </div>
                          </div>
                        );
                      }

                      return (
                        <span className="text-gray-400 text-sm">N/A</span>
                      );
                    }}
                  />
                </DataTable>
              </div>
            )}
          </div>
        </AccordionTab>

        {/* Generate QA Tests Tab */}
        <AccordionTab header="Generate QA Tests" headerClassName="bg-blue-100 dark:bg-blue-900 text-blue-900 dark:text-blue-100 font-bold py-6 text-xl border-2 border-blue-300 dark:border-blue-700 rounded-lg transition hover:bg-blue-200 dark:hover:bg-blue-800 hover:shadow-md mb-6">
          <div className="space-y-10 pt-8 pb-8">
            <div>
              <label className="block text-lg font-bold text-gray-800 dark:text-gray-200 mb-5">
                <span>Select Story</span> {generatedStories.length > 0 && <span className="text-blue-600 ml-2">({generatedStories.length})</span>}
              </label>
              <Dropdown
                value={storyId}
                onChange={(e) => handleStoryChange({ target: { value: e.value } })}
                options={[
                  recentStories.length > 0 ? {
                    label: "📌 Recent Stories",
                    items: recentStories.map((story) => ({
                      label: `⭐ ${story.name || "Untitled"} (ID: ${story.id})`,
                      value: story.id
                    }))
                  } : null,
                  generatedStories.length > 0 ? {
                    label: "All Stories",
                    items: generatedStories.map((story) => ({
                      label: `${story.name || "Untitled"} (ID: ${story.id})`,
                      value: story.id
                    }))
                  } : null
                ].filter(Boolean)}
                optionGroupLabel="label"
                optionGroupChildren="items"
                placeholder="-- Choose a story --"
                className="w-full text-base"
                panelClassName="dark:bg-gray-700 dark:text-white max-h-96 overflow-y-auto"
                showClear
              />
              {generatedStories.length === 0 && epicIdForStories && (
                <p className="text-base text-gray-600 dark:text-gray-400 mt-4">
                  💡 No existing stories found. Generate stories from the Stories tab first.
                </p>
              )}
              {!epicIdForStories && (
                <p className="text-base text-amber-600 dark:text-amber-400 mt-4">
                  ⚠️ Select an epic from the Stories tab first to load stories
                </p>
              )}
            </div>
            <div className="relative group mt-6">
              <Button
                onClick={handleGenerateQA}
                disabled={loadingQA || !storyId || (qaRegenerationAttempts[storyId] || 0) >= 3 || generatedQA.length > 50}
                severity="success"
                className="w-full py-4 text-base font-semibold"
                style={{ backgroundColor: '#3b82f6', borderColor: '#3b82f6' }}
                icon={loadingQA ? undefined : "pi pi-arrow-right"}
                loading={loadingQA}
                label={loadingQA ? `Generating... ${qaProgress}%` : generatedQA.length > 0 ? "Regenerate QA Tests" : "Generate QA Tests"}
              />
              {qaProgress > 0 && loadingQA && (
                <div className="mt-4 w-full bg-gray-300 dark:bg-gray-600 rounded-full h-3">
                  <div 
                    className="bg-blue-500 h-3 rounded-full transition-all duration-300"
                    style={{ width: `${qaProgress}%` }}
                  />
                </div>
              )}
              {(qaRegenerationAttempts[storyId] || 0) >= 3 && (
                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-3 px-4 py-3 bg-gray-800 text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 transition whitespace-nowrap pointer-events-none z-10 font-medium">
                  Max 3 regeneration attempts reached
                </div>
              )}
              {generatedQA.length > 50 && (
                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-3 px-4 py-3 bg-gray-800 text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 transition whitespace-nowrap pointer-events-none z-10 font-medium">
                  Max 50 QA tests reached
                </div>
              )}
            </div>
            {generatedQA.length === 0 && storyId && (
              <p className="text-base text-gray-600 dark:text-gray-400 mt-4">
                💡 No existing QA tests found. Generate QA tests from the selected story.
              </p>
            )}
            {!storyId && generatedStories.length > 0 && (
              <p className="text-base text-amber-600 dark:text-amber-400 mt-4">
                ⚠️ Select a story from the dropdown to load QA tests
              </p>
            )}
            {storyId && (qaRegenerationAttempts[storyId] || 0) > 0 && (qaRegenerationAttempts[storyId] || 0) < 3 && generatedQA.length <= 50 && (
              <p className="text-base text-blue-600 dark:text-blue-400 mt-4 font-semibold">
                ℹ️ Regeneration attempts: {qaRegenerationAttempts[storyId] || 0}/3 (Max 3 allowed) | QA Tests: {generatedQA.length}/50
              </p>
            )}
            {storyId && (qaRegenerationAttempts[storyId] || 0) >= 3 && generatedQA.length <= 50 && (
              <p className="text-base text-red-600 dark:text-red-400 mt-4 font-bold">
                ❌ Maximum regeneration attempts (3) reached. Select a different story to continue.
              </p>
            )}
            {storyId && generatedQA.length > 50 && (
              <p className="text-base text-red-600 dark:text-red-400 mt-4 font-bold">
                ❌ Maximum QA tests count (50) reached. Please visit the QA Page to manage existing tests.
              </p>
            )}
            {storyId && (qaRegenerationAttempts[storyId] || 0) >= 3 && generatedQA.length > 50 && (
              <p className="text-base text-red-600 dark:text-red-400 mt-4 font-bold">
                ❌ Maximum regeneration attempts (3) AND maximum QA tests count (50) reached. Please select a different story or manage existing tests.
              </p>
            )}

            {generatedQA.length > 0 && (
              <div className="pt-10 mt-10 border-t-2 border-gray-300 dark:border-gray-600">
                <h3 className="font-bold text-2xl text-gray-900 dark:text-white mb-8 flex items-center gap-4">
                  <span className="w-2 h-8 bg-blue-500 rounded-full"></span>
                  Generated QA Tests ({generatedQA.length})
                </h3>
                
                <DataTable
                  value={generatedQA}
                  emptyMessage="No QA tests generated"
                  className="p-datatable-striped p-datatable-sm"
                  responsiveLayout="scroll"
                  stripedRows
                  dataKey="id"
                  scrollable
                  scrollHeight="400px"
                  style={{ borderRadius: '0.5rem' }}
                >
                  <Column
                    field="id"
                    header="ID"
                    style={{ width: '80px' }}
                    bodyClassName="text-gray-900 dark:text-gray-100 font-medium"
                  />
                  <Column
                    header="Title"
                    style={{ width: '250px' }}
                    body={(rowData) => {
                      let displayTitle = "QA Test";
                      try {
                        if (typeof rowData.content === 'string') {
                          const parsed = JSON.parse(rowData.content);
                          displayTitle = parsed.title || parsed.name || "QA Test";
                        } else if (rowData.content?.title) {
                          displayTitle = rowData.content.title;
                        } else if (rowData.content?.name) {
                          displayTitle = rowData.content.name;
                        }
                      } catch (e) {
                        displayTitle = String(rowData.content).substring(0, 50);
                      }
                      return displayTitle;
                    }}
                    bodyClassName="text-gray-900 dark:text-gray-100"
                  />
                  <Column
                    header="Test Type"
                    style={{ width: '140px' }}
                    body={(rowData) => {
                      const testType = rowData.test_type || rowData.content?.type || "functional";
                      const typeColors = {
                        "functional": "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
                        "non_functional": "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
                        "api": "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
                      };
                      const colorClass = typeColors[testType] || "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200";
                      return (
                        <span className={`px-2 py-1 rounded text-xs font-semibold whitespace-nowrap ${colorClass}`}>
                          {testType.replace("_", " ").toUpperCase()}
                        </span>
                      );
                    }}
                  />
                </DataTable>
                <p className="text-base text-gray-600 dark:text-gray-400 mt-6 font-medium">
                  💡 For detailed filtering and analysis of QA tests, visit the <a href="/qa" className="font-semibold text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 underline">QA Page</a>
                </p>
              </div>
            )}
          </div>
        </AccordionTab>

        {/* Generate Test Plans Tab */}
        <AccordionTab header="Generate Test Plans" headerClassName="bg-orange-100 dark:bg-orange-900 text-orange-900 dark:text-orange-100 font-bold py-6 text-xl border-2 border-orange-300 dark:border-orange-700 rounded-lg transition hover:bg-orange-200 dark:hover:bg-orange-800 hover:shadow-md mb-6">
          <div className="space-y-10 pt-8 pb-8">
            <div>
              <label className="block text-lg font-bold text-gray-800 dark:text-gray-200 mb-5">
                <span>Select Epic</span> {generatedEpics.length > 0 && <span className="text-orange-600 ml-2">({generatedEpics.length})</span>}
              </label>
              <Dropdown
                value={epicIdForTestPlan}
                onChange={(e) => handleEpicForTestPlanChange({ target: { value: e.value } })}
                options={[
                  recentEpics.length > 0 ? {
                    label: "📌 Recent Epics",
                    items: recentEpics.map((epic) => ({
                      label: `⭐ ${epic.name} (ID: ${epic.id})`,
                      value: epic.id
                    }))
                  } : null,
                  generatedEpics.length > 0 ? {
                    label: "All Epics",
                    items: generatedEpics.map((epic) => ({
                      label: `${epic.name} (ID: ${epic.id})`,
                      value: epic.id
                    }))
                  } : null
                ].filter(Boolean)}
                optionGroupLabel="label"
                optionGroupChildren="items"
                placeholder="-- Choose an epic --"
                className="w-full text-base"
                panelClassName="dark:bg-gray-700 dark:text-white max-h-96 overflow-y-auto"
                showClear
              />
              {generatedEpics.length === 0 && uploadId && (
                <p className="text-base text-gray-600 dark:text-gray-400 mt-4">
                  💡 Generate epics first to create test plans
                </p>
              )}
              {!uploadId && (
                <p className="text-base text-amber-600 dark:text-amber-400 mt-4">
                  ⚠️ Select an upload from the first tab to load epics
                </p>
              )}
            </div>
            <div className="relative group mt-6">
              <Button
                onClick={handleGenerateTestPlan}
                disabled={loadingTestPlan || !epicIdForTestPlan || generatedTestPlans.length > 0}
                severity="success"
                className="w-full py-4 text-base font-semibold"
                style={{ backgroundColor: '#f97316', borderColor: '#f97316' }}
                icon={loadingTestPlan ? undefined : "pi pi-arrow-right"}
                loading={loadingTestPlan}
                label={loadingTestPlan ? `Generating... ${testPlanProgress}%` : "Generate Test Plan"}
              />
              {testPlanProgress > 0 && loadingTestPlan && (
                <div className="mt-4 w-full bg-gray-300 dark:bg-gray-600 rounded-full h-3">
                  <div 
                    className="bg-orange-500 h-3 rounded-full transition-all duration-300"
                    style={{ width: `${testPlanProgress}%` }}
                  />
                </div>
              )}
              {generatedTestPlans.length > 0 && (
                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-3 px-4 py-3 bg-gray-800 text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 transition whitespace-nowrap pointer-events-none z-10 font-medium">
                  Test Plans already present
                </div>
              )}
            </div>
            {generatedTestPlans.length === 0 && epicIdForTestPlan && (
              <p className="text-base text-gray-600 dark:text-gray-400 mt-4">
                💡 No existing test plans found. Generate test plans from the selected epic.
              </p>
            )}
            {!epicIdForTestPlan && generatedEpics.length > 0 && (
              <p className="text-base text-amber-600 dark:text-amber-400 mt-4">
                ⚠️ Select an epic from the dropdown to load test plans
              </p>
            )}

            {generatedTestPlans.length > 0 && (
              <div className="pt-10 mt-10 border-t-2 border-gray-300 dark:border-gray-600">
                <h3 className="font-bold text-2xl text-gray-900 dark:text-white mb-8 flex items-center gap-4">
                  <span className="w-2 h-8 bg-orange-500 rounded-full"></span>
                  Generated Test Plans ({generatedTestPlans.length})
                </h3>
                <DataTable
                  value={generatedTestPlans}
                  emptyMessage="No test plans generated"
                  className="p-datatable-striped p-datatable-sm"
                  responsiveLayout="scroll"
                  stripedRows
                  dataKey="id"
                  scrollable
                  scrollHeight="400px"
                  style={{ borderRadius: '0.5rem' }}
                >
                  <Column
                    field="id"
                    header="ID"
                    style={{ width: '80px' }}
                    bodyClassName="text-gray-900 dark:text-gray-100 font-medium"
                  />
                  <Column
                    header="Title"
                    style={{ width: '300px' }}
                    body={(rowData) => {
                      let displayName = "Test Plan";
                      try {
                        if (typeof rowData.content === 'string') {
                          const parsed = JSON.parse(rowData.content);
                          displayName = parsed.title || parsed.name || "Test Plan";
                        } else if (rowData.content?.title) {
                          displayName = rowData.content.title;
                        } else if (rowData.content?.name) {
                          displayName = rowData.content.name;
                        }
                      } catch (e) {
                        displayName = rowData.name || "Test Plan";
                      }
                      return displayName;
                    }}
                    bodyClassName="text-gray-900 dark:text-gray-100"
                  />
                  <Column
                    header="Confluence Link"
                    style={{ width: '130px' }}
                    body={(rowData) => (
                      rowData.confluence_page_url ? (
                        <Button
                          onClick={() => window.open(rowData.confluence_page_url, '_blank')}
                          label="View"
                          icon="pi pi-external-link"
                          className="p-button-sm p-button-rounded"
                          style={{ backgroundColor: '#f97316', borderColor: '#f97316' }}
                          title="View on Confluence"
                        />
                      ) : (
                        <span className="text-gray-400 text-sm">N/A</span>
                      )
                    )}
                  />
                </DataTable>
              </div>
            )}
          </div>
        </AccordionTab>
      </Accordion>
    </div>
  );
}
