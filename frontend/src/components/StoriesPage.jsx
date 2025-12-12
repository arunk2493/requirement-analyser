import { useEffect, useState } from "react";
import { fetchAllStories } from "../api/api";
import { FaBook, FaSpinner } from "react-icons/fa";
import { DataTable } from "primereact/datatable";
import { Column } from "primereact/column";
import { Button } from "primereact/button";
import { InputText } from "primereact/inputtext";
import { Paginator } from "primereact/paginator";
import { Dropdown } from "primereact/dropdown";

export default function StoriesPage() {
  const [stories, setStories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const [totalStories, setTotalStories] = useState(0);
  const [globalFilter, setGlobalFilter] = useState("");
  const [first, setFirst] = useState(0);
  const [pageSize, setPageSize] = useState(10);

  const loadStories = async () => {
    try {
      setRefreshing(true);
      const page = Math.floor(first / pageSize) + 1;
      const response = await fetchAllStories(page, pageSize);
      setStories(response.data.stories || []);
      setTotalStories(response.data.total_stories || 0);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load stories");
      setStories([]);
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    const initialLoad = async () => {
      try {
        setLoading(true);
        await loadStories();
      } finally {
        setLoading(false);
      }
    };
    initialLoad();
  }, [first, pageSize]);

  // Custom global filter function for ID and story name columns
  const filteredStories = stories.filter((story) => {
    if (!globalFilter.trim()) {
      return true;
    }
    const filterValue = globalFilter.toLowerCase();
    const storyId = String(story.id).toLowerCase();
    const storyName = (story.name || "").toLowerCase();
    
    return storyId.includes(filterValue) || storyName.includes(filterValue);
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <FaBook className="text-4xl text-green-600" />
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
              Stories
            </h1>
          </div>
          <Button
            icon="pi pi-refresh"
            label="Refresh"
            onClick={() => loadStories()}
            disabled={refreshing}
            className="p-button-rounded p-button-text"
            style={{ color: '#22c55e' }}
            title="Refresh stories"
            loading={refreshing}
          />
        </div>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          View all user stories for the selected epic
        </p>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-16">
          <FaSpinner className="text-4xl text-green-500 animate-spin" />
          <p className="ml-4 text-lg text-gray-600 dark:text-gray-400">
            Loading stories...
          </p>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900 border-l-4 border-red-500 p-4 rounded-lg mb-6">
          <p className="text-red-700 dark:text-red-100">
            <span className="font-bold">❌ Error:</span> {error}
          </p>
        </div>
      )}

      {/* Empty State */}
      {!loading && stories.length === 0 && !error && (
        <div className="bg-green-50 dark:bg-green-900 rounded-lg p-12 text-center">
          <p className="text-xl text-green-700 dark:text-green-100">
            📭 No stories found
          </p>
          <p className="text-green-600 dark:text-green-200 mt-2">
            Generate stories to see them here
          </p>
        </div>
      )}

      {/* Stories Table */}
      {!loading && stories.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600 dark:text-gray-400">
              Total Stories: <span className="font-bold text-gray-900 dark:text-white">{totalStories}</span>
            </span>
            <span className="p-input-icon-left">
              <i className="pi pi-search" />
              <InputText
                value={globalFilter}
                onChange={(e) => setGlobalFilter(e.target.value)}
                placeholder="Search stories..."
                className="w-full md:w-auto"
              />
            </span>
          </div>

          <DataTable
            value={filteredStories}
            emptyMessage="No stories found"
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
              headerClassName="font-bold bg-green-500 text-white dark:bg-green-600"
              bodyClassName="text-gray-900 dark:text-gray-100 font-medium"
            />
            <Column
              field="name"
              header="Story Name"
              style={{ width: '300px' }}
              headerClassName="font-bold bg-green-500 text-white dark:bg-green-600"
              bodyClassName="text-gray-900 dark:text-gray-100"
            />
            <Column
              field="created_at"
              header="Created"
              sortable
              style={{ width: '150px' }}
              headerClassName="font-bold bg-green-500 text-white dark:bg-green-600"
              body={(rowData) => new Date(rowData.created_at).toLocaleDateString()}
              bodyClassName="text-gray-600 dark:text-gray-400"
            />
            <Column
              header="Jira"
              style={{ width: '150px' }}
              headerClassName="font-bold bg-green-500 text-white dark:bg-green-600"
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

          {totalStories > pageSize && (
            <div className="mt-6 flex items-center justify-center gap-4">
              <Paginator
                first={first}
                rows={pageSize}
                totalRecords={totalStories}
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
