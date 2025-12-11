import { useEffect, useState } from "react";
import { Accordion, AccordionTab } from "primereact/accordion";
import { DataTable } from "primereact/datatable";
import { Column } from "primereact/column";
import { Button } from "primereact/button";
import {
  fetchAllEpics,
  fetchAllStories,
  fetchAllQA,
  fetchAllTestPlans
} from "../api/api";

import { FaHistory, FaSpinner, FaTimes, FaCopy, FaExternalLinkAlt, FaJira } from "react-icons/fa";

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
        fetchAllEpics(1, pageSize, "created_at", "desc"),
        fetchAllStories(1, pageSize, "created_at", "desc"),
        fetchAllQA(1, pageSize, "created_at", "desc"),
        fetchAllTestPlans(1, pageSize, "created_at", "desc"),
      ]);

      setRecentEpics(epRes.data.data?.epics || epRes.data.epics || []);
      setRecentStories(stRes.data.data?.stories || stRes.data.stories || []);
      setRecentQA(qaRes.data.data?.qa_tests || qaRes.data.qa_tests || qaRes.data.qa || []);
      setRecentTestPlans(tpRes.data.data?.test_plans || tpRes.data.test_plans || []);
    } catch (e) {
      console.error("Failed to load recent lists", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRecentLists();
    
    // Listen for storage changes (user login from another tab/window)
    const handleStorageChange = (e) => {
      if (e.key === 'token' && e.newValue) {
        loadRecentLists();
      }
    };
    
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
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

  const jiraLinkTemplate = (rowData) => {
    if (!rowData.jira_url) return <span className="text-gray-400">-</span>;
    return (
      <Button
        onClick={() => window.open(rowData.jira_url, '_blank')}
        label={rowData.jira_key || 'Open'}
        icon="pi pi-external-link"
        className="p-button-sm p-button-rounded"
        style={{ backgroundColor: '#3b82f6', borderColor: '#3b82f6' }}
        title={`View ${rowData.jira_key} on Jira`}
      />
    );
  };

  const confluenceLinkTemplate = (rowData) => {
    if (!rowData.confluence_page_url) return <span className="text-gray-400">-</span>;
    return (
      <Button
        onClick={() => window.open(rowData.confluence_page_url, '_blank')}
        label="View"
        className="p-button-sm p-button-rounded"
        style={{ backgroundColor: '#10b981', borderColor: '#10b981' }}
        title="View on Confluence"
      />
    );
  };

  const dateTemplate = (rowData) => {
    return <span>{formatDateTime(rowData.created_at)}</span>;
  };

  const scriptButtonTemplate = (rowData) => (
    <div className="flex gap-2 flex-wrap">
      <button
        onClick={() => toggleScript(rowData.id, 'karate')}
        className="px-3 py-2 bg-yellow-200 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 text-xs rounded font-semibold hover:bg-yellow-300 dark:hover:bg-yellow-800 transition"
      >
        🎭 Karate
      </button>
      <button
        onClick={() => toggleScript(rowData.id, 'java')}
        className="px-3 py-2 bg-orange-200 dark:bg-orange-900 text-orange-800 dark:text-orange-200 text-xs rounded font-semibold hover:bg-orange-300 dark:hover:bg-orange-800 transition"
      >
        ☕ Java
      </button>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-6 md:p-10">
      {/* Header */}
      <div className="mb-20 px-8 py-12 bg-gradient-to-r from-orange-50 to-yellow-50 dark:from-gray-800 dark:to-gray-700 rounded-3xl border border-orange-100 dark:border-gray-600 shadow-xl">
        <div className="flex items-center gap-8">
          <div className="p-5 bg-orange-100 dark:bg-orange-900 rounded-xl flex-shrink-0 shadow-md">
            <FaHistory className="text-5xl text-orange-600 dark:text-orange-300" />
          </div>
          <div className="flex-1">
            <h1 className="text-6xl font-bold text-gray-900 dark:text-white mb-4">History</h1>
            <p className="text-gray-600 dark:text-gray-300 text-lg leading-relaxed font-medium">
              Recently created epics, stories, QA tests, and test plans (sorted by creation date - newest first)
            </p>
          </div>
        </div>
      </div>

      {/* Accordion Section Info */}
      <div className="mb-10 px-4">
        <p className="text-lg font-semibold text-gray-700 dark:text-gray-300">Expand sections below to view your history</p>
      </div>

      {/* Style for Accordion */}
      <style>{`
        .p-accordion .p-accordion-header .p-accordion-toggle-icon {
          font-weight: bold;
          margin-right: 0.75rem;
        }
        .p-accordion .p-accordion-header {
          padding-left: 1.5rem !important;
        }
      `}</style>

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-16">
          <FaSpinner className="text-4xl text-orange-500 animate-spin mr-4" />
          <p className="text-lg text-gray-600 dark:text-gray-400">Loading history...</p>
        </div>
      )}

      {/* Accordion Tabs */}
      {!loading && (
        <Accordion className="mb-20" activeIndex={0}>
          {/* Recent Epics Tab */}
          <AccordionTab header="Recent Epics" headerClassName="bg-purple-100 dark:bg-purple-900 text-purple-900 dark:text-purple-100 font-bold py-6 text-xl border-2 border-purple-300 dark:border-purple-700 rounded-lg transition hover:bg-purple-200 dark:hover:bg-purple-800 hover:shadow-md mb-6">
            <div className="pt-4 pb-4">
              {recentEpics.length === 0 ? (
                <div className="text-gray-500 dark:text-gray-400 py-8 text-center">No epics created yet</div>
              ) : (
                <DataTable value={recentEpics} stripedRows scrollable className="dark:text-gray-200">
                  <Column field="name" header="Epic Name" />
                  <Column field="jira_issue_id" header="Jira" body={jiraLinkTemplate} />
                  <Column header="Confluence" body={confluenceLinkTemplate} />
                  <Column field="created_at" header="Created" body={dateTemplate} />
                </DataTable>
              )}
            </div>
          </AccordionTab>

          {/* Recent Stories Tab */}
          <AccordionTab header="Recent Stories" headerClassName="bg-green-100 dark:bg-green-900 text-green-900 dark:text-green-100 font-bold py-6 text-xl border-2 border-green-300 dark:border-green-700 rounded-lg transition hover:bg-green-200 dark:hover:bg-green-800 hover:shadow-md mb-6">
            <div className="pt-4 pb-4">
              {recentStories.length === 0 ? (
                <div className="text-gray-500 dark:text-gray-400 py-8 text-center">No stories created yet</div>
              ) : (
                <DataTable value={recentStories} stripedRows scrollable className="dark:text-gray-200">
                  <Column field="name" header="Story Name" />
                  <Column field="jira_issue_id" header="Jira" body={jiraLinkTemplate} />
                  <Column field="created_at" header="Created" body={dateTemplate} />
                </DataTable>
              )}
            </div>
          </AccordionTab>

          {/* Recent QA Tests Tab */}
          <AccordionTab header="Recent QA Tests" headerClassName="bg-blue-100 dark:bg-blue-900 text-blue-900 dark:text-blue-100 font-bold py-6 text-xl border-2 border-blue-300 dark:border-blue-700 rounded-lg transition hover:bg-blue-200 dark:hover:bg-blue-800 hover:shadow-md mb-6">
            <div className="pt-4 pb-4">
              {recentQA.length === 0 ? (
                <div className="text-gray-500 dark:text-gray-400 py-8 text-center">No QA tests created yet</div>
              ) : (
                <>
                  <DataTable value={recentQA} stripedRows scrollable className="dark:text-gray-200">
                    <Column body={(rowData) => getTestTitle(rowData)} header="Test Name" />
                    <Column header="Scripts" body={scriptButtonTemplate} />
                    <Column field="created_at" header="Created" body={dateTemplate} />
                  </DataTable>

                  {/* Modal for Automation Scripts */}
                  {Object.keys(expandedScripts).map(qaId => {
                    const qa = recentQA.find(q => q.id === Number.parseInt(qaId, 10));
                    if (!expandedScripts[qaId] || !qa) return null;
                    return (
                      <div key={qaId} className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                        <div className="bg-white dark:bg-gray-900 rounded-lg shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-auto">
                          {/* Header */}
                          <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
                            <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                              {scriptLanguage[qaId] === 'karate' ? '🎭 Karate Script' : '☕ Java Script'} - {getTestTitle(qa)}
                            </h3>
                            <button
                              onClick={() => toggleScript(qa.id, scriptLanguage[qaId])}
                              className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                            >
                              <FaTimes className="text-xl" />
                            </button>
                          </div>

                          {/* Body */}
                          <div className="p-6">
                            <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                              <code>
                                {scriptLanguage[qaId] === 'karate' 
                                  ? generateKarateScript(qa) 
                                  : generateJavaScript(qa)}
                              </code>
                            </pre>
                          </div>

                          {/* Footer */}
                          <div className="flex items-center justify-between p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
                            <button
                              onClick={() => copyToClipboard(
                                scriptLanguage[qaId] === 'karate' 
                                  ? generateKarateScript(qa) 
                                  : generateJavaScript(qa),
                                qa.id
                              )}
                              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg flex items-center gap-2 transition"
                            >
                              <FaCopy className="text-sm" />
                              Copy
                            </button>
                            {copyNotification[qaId] && (
                              <span className="text-green-600 dark:text-green-400 text-sm">✓ Copied to clipboard!</span>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </>
              )}
            </div>
          </AccordionTab>

          {/* Recent Test Plans Tab */}
          <AccordionTab header="Recent Test Plans" headerClassName="bg-orange-100 dark:bg-orange-900 text-orange-900 dark:text-orange-100 font-bold py-6 text-xl border-2 border-orange-300 dark:border-orange-700 rounded-lg transition hover:bg-orange-200 dark:hover:bg-orange-800 hover:shadow-md mb-6">
            <div className="pt-4 pb-4">
              {recentTestPlans.length === 0 ? (
                <div className="text-gray-500 dark:text-gray-400 py-8 text-center">No test plans created yet</div>
              ) : (
                <DataTable value={recentTestPlans} stripedRows scrollable className="dark:text-gray-200">
                  <Column body={(rowData) => getTestPlanTitle(rowData)} header="Test Plan Name" />
                  <Column header="Confluence" body={confluenceLinkTemplate} />
                  <Column field="created_at" header="Created" body={dateTemplate} />
                </DataTable>
              )}
            </div>
          </AccordionTab>
        </Accordion>
      )}
    </div>
  );
}
