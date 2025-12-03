import { useEffect, useState } from "react";
import {
  fetchAllEpics,
  fetchAllStories,
  fetchAllQA,
  fetchAllTestPlans
} from "../api/api";

import { FaHistory, FaSpinner, FaTimes, FaCopy } from "react-icons/fa";

export default function History() {
  // Recent lists
  const [recentEpics, setRecentEpics] = useState([]);
  const [recentStories, setRecentStories] = useState([]);
  const [recentQA, setRecentQA] = useState([]);
  const [recentTestPlans, setRecentTestPlans] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Modal state for automation scripts
  const [expandedScripts, setExpandedScripts] = useState({});
  const [scriptLanguage, setScriptLanguage] = useState({});
  const [copyNotification, setCopyNotification] = useState({});

  const pageSize = 5;

  const loadRecentLists = async () => {
    try {
      setLoading(true);
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
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRecentLists();
  }, []);

  const getTestTitle = (qa) => {
    if (typeof qa.content === 'string') {
      try {
        const parsed = JSON.parse(qa.content);
        return parsed.title || parsed.name || 'QA Test';
      } catch {
        return qa.content.substring(0, 30);
      }
    }
    return qa.content?.title || qa.content?.name || 'QA Test';
  };

  const getTestPlanTitle = (tp) => {
    if (typeof tp.content === 'string') {
      try {
        const parsed = JSON.parse(tp.content);
        return parsed.title || parsed.name || 'Test Plan';
      } catch {
        return tp.content.substring(0, 30);
      }
    }
    return tp.content?.title || tp.content?.name || 'Test Plan';
  };

  const formatDateTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true
    });
  };

  const generateKarateScript = (test) => {
    const title = getTestTitle(test);
    const description = getTestDescription(test);
    return `Feature: ${title}
  
  Background:
    * url 'http://api.example.com'
    * header Content-Type = 'application/json'
    * header Accept = 'application/json'

  Scenario: ${description || 'Test Scenario'}
    Given path '/endpoint'
    When method get
    Then status 200
    And match response == '#object'`;
  };

  const generateJavaScript = (test) => {
    const title = getTestTitle(test);
    return `import io.restassured.RestAssured;
import io.restassured.response.Response;
import org.junit.Before;
import org.junit.Test;
import static io.restassured.RestAssured.*;
import static org.hamcrest.Matchers.*;

public class ${title.replace(/\\s+/g, '')}Test {
  
  @Before
  public void setUp() {
    RestAssured.baseURI = "http://api.example.com";
  }

  @Test
  public void test${title.replace(/\\s+/g, '')}() {
    given()
      .header("Content-Type", "application/json")
      .header("Accept", "application/json")
    .when()
      .get("/endpoint")
    .then()
      .statusCode(200)
      .body(containsString("expected"));
  }
}`;
  };

  const getTestDescription = (qa) => {
    if (typeof qa.content === 'string') {
      try {
        const parsed = JSON.parse(qa.content);
        return parsed.description || parsed.test_case || '';
      } catch {
        return qa.content.substring(0, 60);
      }
    }
    return qa.content?.description || qa.content?.test_case || '';
  };

  const copyToClipboard = (text, qaId) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopyNotification(prev => ({ ...prev, [qaId]: true }));
      setTimeout(() => {
        setCopyNotification(prev => ({ ...prev, [qaId]: false }));
      }, 2000);
    });
  };

  const toggleScript = (qaId, language) => {
    setExpandedScripts(prev => ({ ...prev, [qaId]: !prev[qaId] }));
    setScriptLanguage(prev => ({ ...prev, [qaId]: language }));
  };

  return (
    <div className="min-h-screen p-8 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">

      {/* Header */}
      <div className="mb-8 flex items-center gap-3">
        <FaHistory className="text-4xl text-orange-600" />
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white">📜 History</h1>
      </div>
      <p className="text-gray-600 dark:text-gray-400 mb-8">Recently created epics, stories, QA tests, and test plans (sorted by creation date - newest first)</p>

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-16">
          <FaSpinner className="text-4xl text-orange-500 animate-spin mr-4" />
          <p className="text-lg text-gray-600 dark:text-gray-400">Loading history...</p>
        </div>
      )}

      {/* Content Grid */}
      {!loading && (
        <div className="grid grid-cols-1 gap-6">

          {/* Row 1: Epics and Stories */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Recent Epics */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-bold text-purple-600 mb-4">📚 Recent Epics (Top 5)</h2>
              {recentEpics.length === 0 ? (
                <div className="text-gray-500 dark:text-gray-400 py-8 text-center">No epics created yet</div>
              ) : (
                <div className="space-y-3">
                  {recentEpics.map((epic, idx) => (
                    <div key={epic.id} className="p-3 bg-purple-50 dark:bg-gray-700 rounded-lg border border-purple-200 dark:border-gray-600 hover:shadow-md transition">
                      <div className="flex items-start justify-between mb-2">
                        <p className="font-semibold text-gray-900 dark:text-white">{idx + 1}. {epic.name}</p>
                        {epic.confluence_page_url && (
                          <a 
                            href={epic.confluence_page_url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="px-2 py-1 bg-purple-200 dark:bg-purple-900 text-purple-800 dark:text-purple-200 text-xs rounded hover:bg-purple-300 dark:hover:bg-purple-800 transition"
                          >
                            🔗 View
                          </a>
                        )}
                      </div>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {formatDateTime(epic.created_at)}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Recent Stories */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-bold text-green-600 mb-4">📖 Recent Stories (Top 5)</h2>
              {recentStories.length === 0 ? (
                <div className="text-gray-500 dark:text-gray-400 py-8 text-center">No stories created yet</div>
              ) : (
                <div className="space-y-3">
                  {recentStories.map((story, idx) => (
                    <div key={story.id} className="p-3 bg-green-50 dark:bg-gray-700 rounded-lg border border-green-200 dark:border-gray-600 hover:shadow-md transition">
                      <div className="flex items-start justify-between mb-2">
                        <p className="font-semibold text-gray-900 dark:text-white">{idx + 1}. {story.name || 'Story ' + story.id}</p>
                        {story.confluence_page_url && (
                          <a 
                            href={story.confluence_page_url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="px-2 py-1 bg-green-200 dark:bg-green-900 text-green-800 dark:text-green-200 text-xs rounded hover:bg-green-300 dark:hover:bg-green-800 transition"
                          >
                            🔗 View
                          </a>
                        )}
                      </div>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {formatDateTime(story.created_at)}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Row 2: QA Tests (Full width) */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold text-blue-600 mb-4">✅ Recent QA Tests (Top 5)</h2>
            {recentQA.length === 0 ? (
              <div className="text-gray-500 dark:text-gray-400 py-8 text-center">No QA tests created yet</div>
            ) : (
              <div className="space-y-3">
                {recentQA.map((qa, idx) => (
                  <div key={qa.id} className="p-4 bg-blue-50 dark:bg-gray-700 rounded-lg border border-blue-200 dark:border-gray-600 hover:shadow-md transition">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <p className="font-semibold text-gray-900 dark:text-white">{idx + 1}. {getTestTitle(qa)}</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{formatDateTime(qa.created_at)}</p>
                      </div>
                      <div className="flex gap-2 flex-wrap justify-end">
                        {qa.confluence_page_url && (
                          <a 
                            href={qa.confluence_page_url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="px-2 py-1 bg-blue-200 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs rounded hover:bg-blue-300 dark:hover:bg-blue-800 transition"
                          >
                            🔗 View
                          </a>
                        )}
                        <button
                          onClick={() => toggleScript(qa.id, 'karate')}
                          className="px-2 py-1 bg-yellow-200 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 text-xs rounded hover:bg-yellow-300 dark:hover:bg-yellow-800 transition"
                        >
                          🎭 Karate
                        </button>
                        <button
                          onClick={() => toggleScript(qa.id, 'java')}
                          className="px-2 py-1 bg-orange-200 dark:bg-orange-900 text-orange-800 dark:text-orange-200 text-xs rounded hover:bg-orange-300 dark:hover:bg-orange-800 transition"
                        >
                          ☕ Java
                        </button>
                      </div>
                    </div>

                    {/* Modal for Automation Scripts */}
                    {expandedScripts[qa.id] && (
                      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                        <div className="bg-white dark:bg-gray-900 rounded-lg shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-auto">
                          {/* Header */}
                          <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
                            <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                              {scriptLanguage[qa.id] === 'karate' ? '🎭 Karate Script' : '☕ Java Script'} - {getTestTitle(qa)}
                            </h3>
                            <button
                              onClick={() => toggleScript(qa.id, scriptLanguage[qa.id])}
                              className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                            >
                              <FaTimes className="text-xl" />
                            </button>
                          </div>

                          {/* Body */}
                          <div className="p-6">
                            <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                              <code>
                                {scriptLanguage[qa.id] === 'karate' 
                                  ? generateKarateScript(qa) 
                                  : generateJavaScript(qa)}
                              </code>
                            </pre>
                          </div>

                          {/* Footer */}
                          <div className="flex items-center justify-between p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
                            <button
                              onClick={() => copyToClipboard(
                                scriptLanguage[qa.id] === 'karate' 
                                  ? generateKarateScript(qa) 
                                  : generateJavaScript(qa),
                                qa.id
                              )}
                              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg flex items-center gap-2 transition"
                            >
                              <FaCopy className="text-sm" />
                              Copy
                            </button>
                            {copyNotification[qa.id] && (
                              <span className="text-green-600 dark:text-green-400 text-sm">✓ Copied to clipboard!</span>
                            )}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Row 3: Test Plans (Full width) */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold text-orange-600 mb-4">📋 Recent Test Plans (Top 5)</h2>
            {recentTestPlans.length === 0 ? (
              <div className="text-gray-500 dark:text-gray-400 py-8 text-center">No test plans created yet</div>
            ) : (
              <div className="space-y-3">
                {recentTestPlans.map((testPlan, idx) => (
                  <div key={testPlan.id} className="p-3 bg-orange-50 dark:bg-gray-700 rounded-lg border border-orange-200 dark:border-gray-600 hover:shadow-md transition">
                    <div className="flex items-start justify-between mb-2">
                      <p className="font-semibold text-gray-900 dark:text-white">{idx + 1}. {getTestPlanTitle(testPlan)}</p>
                      {testPlan.confluence_page_url && (
                        <a 
                          href={testPlan.confluence_page_url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="px-2 py-1 bg-orange-200 dark:bg-orange-900 text-orange-800 dark:text-orange-200 text-xs rounded hover:bg-orange-300 dark:hover:bg-orange-800 transition"
                        >
                          🔗 View
                        </a>
                      )}
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {formatDateTime(testPlan.created_at)}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>

        </div>
      )}
    </div>
  );
}