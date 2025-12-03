import { useEffect, useState } from "react";
import axios from "axios";
import { Card } from "primereact/card";
import { Button } from "primereact/button";
import { InputNumber } from "primereact/inputnumber";
import { InputText } from "primereact/inputtext";
import { Toast } from "primereact/toast";
import { ProgressSpinner } from "primereact/progressspinner";
import { Divider } from "primereact/divider";
import { TabView, TabPanel } from "primereact/tabview";
import { DataTable } from "primereact/datatable";
import { Column } from "primereact/column";
import { useRef } from "react";

const API_BASE = "http://localhost:8000";

export default function AgenticAIPage() {
  const [uploadId, setUploadId] = useState(null);
  const [epicId, setEpicId] = useState(null);
  const [storyId, setStoryId] = useState(null);
  const [ragQuery, setRagQuery] = useState("");

  const [loadingEpics, setLoadingEpics] = useState(false);
  const [loadingStories, setLoadingStories] = useState(false);
  const [loadingQA, setLoadingQA] = useState(false);
  const [loadingRAG, setLoadingRAG] = useState(false);
  const [loadingWorkflow, setLoadingWorkflow] = useState(false);

  const [epics, setEpics] = useState([]);
  const [stories, setStories] = useState([]);
  const [qaTests, setQATests] = useState([]);
  const [ragResults, setRagResults] = useState([]);

  const toastRef = useRef(null);

  const showToast = (severity, summary, detail) => {
    toastRef.current?.show({ severity, summary, detail, life: 3000 });
  };

  // Generate Epics
  const onGenerateEpics = async () => {
    if (!uploadId) {
      showToast("error", "Error", "Please enter an Upload ID");
      return;
    }
    try {
      setLoadingEpics(true);
      const res = await axios.post(`${API_BASE}/agents/epic/generate`, {
        upload_id: uploadId,
      });
      setEpics(res.data.data?.epics || []);
      showToast("success", "Success", res.data.message);
    } catch (e) {
      showToast("error", "Error", e.response?.data?.detail || e.message);
    } finally {
      setLoadingEpics(false);
    }
  };

  // Generate Stories
  const onGenerateStories = async () => {
    if (!epicId) {
      showToast("error", "Error", "Please enter an Epic ID");
      return;
    }
    try {
      setLoadingStories(true);
      const res = await axios.post(`${API_BASE}/agents/story/generate`, {
        epic_id: epicId,
      });
      setStories(res.data.data?.stories || []);
      showToast("success", "Success", res.data.message);
    } catch (e) {
      showToast("error", "Error", e.response?.data?.detail || e.message);
    } finally {
      setLoadingStories(false);
    }
  };

  // Generate QA
  const onGenerateQA = async () => {
    if (!storyId) {
      showToast("error", "Error", "Please enter a Story ID");
      return;
    }
    try {
      setLoadingQA(true);
      const res = await axios.post(`${API_BASE}/agents/qa/generate`, {
        story_id: storyId,
      });
      setQATests(res.data.data?.qa_tests || []);
      showToast("success", "Success", res.data.message);
    } catch (e) {
      showToast("error", "Error", e.response?.data?.detail || e.message);
    } finally {
      setLoadingQA(false);
    }
  };

  // RAG Search
  const onRAGSearch = async () => {
    if (!ragQuery) {
      showToast("error", "Error", "Please enter a search query");
      return;
    }
    try {
      setLoadingRAG(true);
      const res = await axios.post(`${API_BASE}/agents/rag/search`, {
        query: ragQuery,
        upload_id: uploadId || null,
        top_k: 5,
      });
      setRagResults(res.data.data?.documents || []);
      showToast("success", "Success", res.data.message);
    } catch (e) {
      showToast("error", "Error", e.response?.data?.detail || e.message);
    } finally {
      setLoadingRAG(false);
    }
  };

  // Execute Full Workflow
  const onExecuteWorkflow = async () => {
    if (!uploadId) {
      showToast("error", "Error", "Please enter an Upload ID");
      return;
    }
    try {
      setLoadingWorkflow(true);
      const res = await axios.post(`${API_BASE}/agents/workflow/execute`, {
        upload_id: uploadId,
      });
      const workflowData = res.data.data;
      setEpics(workflowData.epics || []);
      setStories(workflowData.stories || []);
      setQATests(workflowData.qa || []);
      showToast("success", "Success", res.data.message);
    } catch (e) {
      showToast("error", "Error", e.response?.data?.detail || e.message);
    } finally {
      setLoadingWorkflow(false);
    }
  };

  return (
    <div className="p-4">
      <Toast ref={toastRef} />

      <div className="mb-4">
        <h1 className="text-3xl font-bold">Agentic AI Requirement Analyzer</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Use specialized agents to generate epics, stories, QA tests, and retrieve documents from RAG
        </p>
      </div>

      <TabView>
        {/* Epic Generation */}
        <TabPanel header="Generate Epics" leftIcon="pi pi-book">
          <Card className="mb-4">
            <div className="flex flex-col gap-4">
              <div>
                <label className="block font-semibold mb-2">Upload ID</label>
                <InputNumber
                  value={uploadId}
                  onValueChange={(e) => setUploadId(e.value)}
                  placeholder="Enter upload ID"
                  className="w-full"
                />
              </div>

              <Button
                label="Generate Epics"
                icon="pi pi-play"
                onClick={onGenerateEpics}
                loading={loadingEpics}
                disabled={!uploadId || loadingEpics}
                className="p-button-primary"
              />

              {epics.length > 0 && (
                <div className="mt-4">
                  <h3 className="font-semibold mb-2">Generated Epics</h3>
                  <DataTable value={epics} responsiveLayout="scroll">
                    <Column field="id" header="ID" />
                    <Column field="name" header="Name" />
                    <Column
                      field="confluence_page_url"
                      header="Confluence Link"
                      body={(rowData) =>
                        rowData.confluence_page_url ? (
                          <a
                            href={rowData.confluence_page_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 underline"
                          >
                            View
                          </a>
                        ) : (
                          "N/A"
                        )
                      }
                    />
                  </DataTable>
                </div>
              )}
            </div>
          </Card>
        </TabPanel>

        {/* Story Generation */}
        <TabPanel header="Generate Stories" leftIcon="pi pi-list">
          <Card className="mb-4">
            <div className="flex flex-col gap-4">
              <div>
                <label className="block font-semibold mb-2">Epic ID</label>
                <InputNumber
                  value={epicId}
                  onValueChange={(e) => setEpicId(e.value)}
                  placeholder="Enter epic ID"
                  className="w-full"
                />
              </div>

              <Button
                label="Generate Stories"
                icon="pi pi-play"
                onClick={onGenerateStories}
                loading={loadingStories}
                disabled={!epicId || loadingStories}
                className="p-button-primary"
              />

              {stories.length > 0 && (
                <div className="mt-4">
                  <h3 className="font-semibold mb-2">Generated Stories</h3>
                  <DataTable value={stories} responsiveLayout="scroll">
                    <Column field="id" header="ID" />
                    <Column field="name" header="Name" />
                    <Column
                      field="content"
                      header="Content"
                      body={(rowData) =>
                        <span className="text-sm line-clamp-2">
                          {JSON.stringify(rowData.content).substring(0, 100)}...
                        </span>
                      }
                    />
                  </DataTable>
                </div>
              )}
            </div>
          </Card>
        </TabPanel>

        {/* QA Generation */}
        <TabPanel header="Generate QA" leftIcon="pi pi-check-square">
          <Card className="mb-4">
            <div className="flex flex-col gap-4">
              <div>
                <label className="block font-semibold mb-2">Story ID</label>
                <InputNumber
                  value={storyId}
                  onValueChange={(e) => setStoryId(e.value)}
                  placeholder="Enter story ID"
                  className="w-full"
                />
              </div>

              <Button
                label="Generate QA Tests"
                icon="pi pi-play"
                onClick={onGenerateQA}
                loading={loadingQA}
                disabled={!storyId || loadingQA}
                className="p-button-primary"
              />

              {qaTests.length > 0 && (
                <div className="mt-4">
                  <h3 className="font-semibold mb-2">Generated QA Tests</h3>
                  <DataTable value={qaTests} responsiveLayout="scroll">
                    <Column field="id" header="ID" />
                    <Column field="title" header="Title" />
                    <Column
                      field="content"
                      header="Content Preview"
                      body={(rowData) =>
                        <span className="text-sm line-clamp-2">
                          {JSON.stringify(rowData.content).substring(0, 100)}...
                        </span>
                      }
                    />
                  </DataTable>
                </div>
              )}
            </div>
          </Card>
        </TabPanel>

        {/* RAG Retrieval */}
        <TabPanel header="RAG Search" leftIcon="pi pi-search">
          <Card className="mb-4">
            <div className="flex flex-col gap-4">
              <div>
                <label className="block font-semibold mb-2">Search Query</label>
                <InputText
                  value={ragQuery}
                  onChange={(e) => setRagQuery(e.target.value)}
                  placeholder="Enter search query"
                  className="w-full"
                />
              </div>

              <div>
                <label className="block font-semibold mb-2">Upload ID (Optional)</label>
                <InputNumber
                  value={uploadId}
                  onValueChange={(e) => setUploadId(e.value)}
                  placeholder="Filter by upload ID"
                  className="w-full"
                />
              </div>

              <Button
                label="Search Documents"
                icon="pi pi-search"
                onClick={onRAGSearch}
                loading={loadingRAG}
                disabled={!ragQuery || loadingRAG}
                className="p-button-primary"
              />

              {ragResults.length > 0 && (
                <div className="mt-4">
                  <h3 className="font-semibold mb-2">Retrieved Documents</h3>
                  <div className="space-y-3">
                    {ragResults.map((doc, idx) => (
                      <Card key={idx} className="p-3 bg-blue-50 dark:bg-blue-900">
                        <p className="text-sm font-semibold mb-1">Document {idx + 1}</p>
                        <p className="text-sm mb-2">{doc.content || "No content"}</p>
                        <p className="text-xs text-gray-600">
                          Similarity: {(doc.similarity || 0).toFixed(3)}
                        </p>
                      </Card>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </Card>
        </TabPanel>

        {/* Workflow Execution */}
        <TabPanel header="Full Workflow" leftIcon="pi pi-play">
          <Card className="mb-4">
            <div className="flex flex-col gap-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Execute the complete workflow: Upload → Generate Epics → Generate Stories → Generate QA
              </p>

              <div>
                <label className="block font-semibold mb-2">Upload ID</label>
                <InputNumber
                  value={uploadId}
                  onValueChange={(e) => setUploadId(e.value)}
                  placeholder="Enter upload ID"
                  className="w-full"
                />
              </div>

              <Button
                label="Execute Full Workflow"
                icon="pi pi-arrow-right"
                onClick={onExecuteWorkflow}
                loading={loadingWorkflow}
                disabled={!uploadId || loadingWorkflow}
                className="p-button-success p-button-lg"
              />

              {loadingWorkflow && (
                <div className="flex justify-center mt-4">
                  <ProgressSpinner />
                </div>
              )}

              {(epics.length > 0 || stories.length > 0 || qaTests.length > 0) && (
                <div className="mt-6 space-y-4">
                  <Divider />
                  <h3 className="font-semibold text-lg">Workflow Results</h3>

                  {epics.length > 0 && (
                    <Card className="p-3 bg-purple-50 dark:bg-purple-900">
                      <h4 className="font-semibold mb-2">Epics ({epics.length})</h4>
                      <DataTable value={epics.slice(0, 3)} responsiveLayout="scroll">
                        <Column field="id" header="ID" />
                        <Column field="name" header="Name" />
                      </DataTable>
                    </Card>
                  )}

                  {stories.length > 0 && (
                    <Card className="p-3 bg-green-50 dark:bg-green-900">
                      <h4 className="font-semibold mb-2">Stories ({stories.length})</h4>
                      <DataTable value={stories.slice(0, 3)} responsiveLayout="scroll">
                        <Column field="id" header="ID" />
                        <Column field="name" header="Name" />
                      </DataTable>
                    </Card>
                  )}

                  {qaTests.length > 0 && (
                    <Card className="p-3 bg-blue-50 dark:bg-blue-900">
                      <h4 className="font-semibold mb-2">QA Tests ({qaTests.length})</h4>
                      <DataTable value={qaTests.slice(0, 3)} responsiveLayout="scroll">
                        <Column field="id" header="ID" />
                        <Column field="title" header="Title" />
                      </DataTable>
                    </Card>
                  )}
                </div>
              )}
            </div>
          </Card>
        </TabPanel>
      </TabView>
    </div>
  );
}
