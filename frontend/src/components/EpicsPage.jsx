import { useEffect, useState } from "react";
import { fetchAllEpics } from "../api/api";
import { FaBook, FaSpinner } from "react-icons/fa";
import { DataTable } from "primereact/datatable";
import { Column } from "primereact/column";
import { Button } from "primereact/button";
import { InputText } from "primereact/inputtext";
import { Paginator } from "primereact/paginator";
import { Dropdown } from "primereact/dropdown";

export default function EpicsPage() {
  const [epics, setEpics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const [totalEpics, setTotalEpics] = useState(0);
  const [globalFilter, setGlobalFilter] = useState("");
  const [first, setFirst] = useState(0);
  const [pageSize, setPageSize] = useState(10);

  const loadEpics = async () => {
    try {
      setRefreshing(true);
      const page = Math.floor(first / pageSize) + 1;
      const response = await fetchAllEpics(page, pageSize);
      setEpics(response.data.epics || []);
      setTotalEpics(response.data.total_epics || 0);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load epics");
      setEpics([]);
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    const initialLoad = async () => {
      try {
        setLoading(true);
        await loadEpics();
      } finally {
        setLoading(false);
      }
    };
    initialLoad();
  }, [first, pageSize]);

  // Custom global filter function for ID and epic name columns
  const filteredEpics = epics.filter((epic) => {
    if (!globalFilter.trim()) {
      return true;
    }
    const filterValue = globalFilter.toLowerCase();
    const epicId = String(epic.id).toLowerCase();
    const epicName = (epic.name || "").toLowerCase();
    
    return epicId.includes(filterValue) || epicName.includes(filterValue);
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <FaBook className="text-4xl text-purple-600" />
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white">Epics</h1>
          </div>
          <Button
            icon="pi pi-refresh"
            label="Refresh"
            onClick={() => loadEpics()}
            disabled={refreshing}
            className="p-button-rounded p-button-text"
            style={{ color: '#a855f7' }}
            title="Refresh epics"
            loading={refreshing}
          />
        </div>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          View all epics with their detailed information and Confluence links
        </p>
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-16">
          <FaSpinner className="text-4xl text-blue-500 animate-spin" />
          <p className="ml-4 text-lg text-gray-600 dark:text-gray-400">Loading epics...</p>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900 border-l-4 border-red-500 p-4 rounded-lg mb-6">
          <p className="text-red-700 dark:text-red-100">
            <span className="font-bold">❌ Error:</span> {error}
          </p>
        </div>
      )}

      {/* Empty */}
      {!loading && epics.length === 0 && !error && (
        <div className="bg-blue-50 dark:bg-blue-900 rounded-lg p-12 text-center">
          <p className="text-xl text-blue-700 dark:text-blue-100">📭 No epics found</p>
          <p className="text-blue-600 dark:text-blue-200 mt-2">Generate epics from your uploaded requirements to see them here</p>
        </div>
      )}

      {/* Table */}
      {!loading && epics.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600 dark:text-gray-400">
              Total Epics: <span className="font-bold text-gray-900 dark:text-white">{totalEpics}</span>
            </span>
            <span className="p-input-icon-left">
              <i className="pi pi-search" />
              <InputText
                value={globalFilter}
                onChange={(e) => setGlobalFilter(e.target.value)}
                placeholder="Search epics..."
                className="w-full md:w-auto"
              />
            </span>
          </div>

          <DataTable
            value={filteredEpics}
            emptyMessage="No epics found"
            className="p-datatable-striped p-datatable-sm"
            responsiveLayout="scroll"
            stripedRows
            loading={refreshing}
            dataKey="id"
            scrollable
            scrollHeight="600px"
            style={{ borderRadius: '0.5rem' }}
          >
            <Column
              field="id"
              header="ID"
              sortable
              style={{ width: '80px' }}
              headerClassName="font-bold bg-blue-500 text-white dark:bg-blue-600"
              bodyClassName="text-gray-900 dark:text-gray-100 font-medium"
            />
            <Column
              field="name"
              header="Epic Name"
              style={{ width: '300px' }}
              headerClassName="font-bold bg-blue-500 text-white dark:bg-blue-600"
              bodyClassName="text-gray-900 dark:text-gray-100"
            />
            <Column
              field="created_at"
              header="Created"
              sortable
              style={{ width: '150px' }}
              headerClassName="font-bold bg-blue-500 text-white dark:bg-blue-600"
              body={(rowData) => new Date(rowData.created_at).toLocaleDateString()}
              bodyClassName="text-gray-600 dark:text-gray-400"
            />
            <Column
              header="Confluence"
              style={{ width: '120px' }}
              headerClassName="font-bold bg-blue-500 text-white dark:bg-blue-600"
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
              header="Jira"
              style={{ width: '150px' }}
              headerClassName="font-bold bg-blue-500 text-white dark:bg-blue-600"
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
          </DataTable>

          {totalEpics > pageSize && (
            <div className="mt-6 flex items-center justify-center gap-4">
              <Paginator
                first={first}
                rows={pageSize}
                totalRecords={totalEpics}
                onPageChange={(e) => {
                  setFirst(e.first);
                }}
                template="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink"
              />
              <Dropdown
                value={pageSize}
                onChange={(e) => {
                  setPageSize(e.value);
                  setFirst(0);
                }}
                options={[5, 10, 20, 50]}
                className="p-dropdown-compact"
                style={{ width: '70px' }}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
