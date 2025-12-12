import { useEffect, useState } from "react";
import { fetchAllTestPlans } from "../api/api";
import { FaFileAlt, FaSpinner } from "react-icons/fa";
import { DataTable } from "primereact/datatable";
import { Column } from "primereact/column";
import { Button } from "primereact/button";
import { InputText } from "primereact/inputtext";
import { Paginator } from "primereact/paginator";
import { Dropdown } from "primereact/dropdown";

export default function TestPlansPage() {
  const [testplans, setTestPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const [totalTestPlans, setTotalTestPlans] = useState(0);
  const [globalFilter, setGlobalFilter] = useState("");
  const [first, setFirst] = useState(0);
  const [pageSize, setPageSize] = useState(10);

  const loadTestPlans = async () => {
    try {
      setRefreshing(true);
      const page = Math.floor(first / pageSize) + 1;
      const response = await fetchAllTestPlans(page, pageSize);
      setTestPlans(response.data.test_plans || []);
      setTotalTestPlans(response.data.total_test_plans || 0);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load test plans");
      setTestPlans([]);
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    const initialLoad = async () => {
      try {
        setLoading(true);
        await loadTestPlans();
      } finally {
        setLoading(false);
      }
    };
    initialLoad();
  }, [first, pageSize]);

  // Custom global filter function for ID and test plan name columns
  const filteredTestPlans = testplans.filter((plan) => {
    if (!globalFilter.trim()) {
      return true;
    }
    const filterValue = globalFilter.toLowerCase();
    const planId = String(plan.id).toLowerCase();
    const planTitle = (plan.title || "").toLowerCase();
    
    return planId.includes(filterValue) || planTitle.includes(filterValue);
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <FaFileAlt className="text-4xl text-orange-600" />
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
              Test Plans
            </h1>
          </div>
          <Button
            icon="pi pi-refresh"
            label="Refresh"
            onClick={() => loadTestPlans()}
            disabled={refreshing}
            className="p-button-rounded p-button-text"
            style={{ color: '#f97316' }}
            title="Refresh test plans"
            loading={refreshing}
          />
        </div>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          View all test plans for the selected epic with Confluence links
        </p>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-16">
          <FaSpinner className="text-4xl text-orange-500 animate-spin" />
          <p className="ml-4 text-lg text-gray-600 dark:text-gray-400">
            Loading test plans...
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
      {!loading && testplans.length === 0 && !error && (
        <div className="bg-orange-50 dark:bg-orange-900 rounded-lg p-12 text-center">
          <p className="text-xl text-orange-700 dark:text-orange-100">
            📭 No test plans found
          </p>
          <p className="text-orange-600 dark:text-orange-200 mt-2">
            Generate test plans to see them here
          </p>
        </div>
      )}

      {/* Test Plans Table */}
      {!loading && testplans.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600 dark:text-gray-400">
              Total Test Plans: <span className="font-bold text-gray-900 dark:text-white">{totalTestPlans}</span>
            </span>
            <span className="p-input-icon-left">
              <i className="pi pi-search" />
              <InputText
                value={globalFilter}
                onChange={(e) => setGlobalFilter(e.target.value)}
                placeholder="Search test plans..."
                className="w-full md:w-auto"
              />
            </span>
          </div>

          <DataTable
            value={filteredTestPlans}
            emptyMessage="No test plans found"
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
              headerClassName="font-bold bg-orange-500 text-white dark:bg-orange-600"
              bodyClassName="text-gray-900 dark:text-gray-100 font-medium"
            />
            <Column
              field="title"
              header="Title"
              style={{ width: '300px' }}
              headerClassName="font-bold bg-orange-500 text-white dark:bg-orange-600"
              body={(rowData) => rowData.title || (rowData.content?.title ?? (typeof rowData.content === 'string' ? rowData.content.substring(0, 50) : JSON.stringify(rowData.content).substring(0, 50)))}
              bodyClassName="text-gray-900 dark:text-gray-100"
            />
            <Column
              field="created_at"
              header="Created"
              sortable
              style={{ width: '150px' }}
              headerClassName="font-bold bg-orange-500 text-white dark:bg-orange-600"
              body={(rowData) => new Date(rowData.created_at).toLocaleDateString()}
              bodyClassName="text-gray-600 dark:text-gray-400"
            />
            <Column
              header="Confluence"
              style={{ width: '150px' }}
              headerClassName="font-bold bg-orange-500 text-white dark:bg-orange-600"
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

          {totalTestPlans > pageSize && (
            <div className="mt-6 flex items-center justify-center gap-4">
              <Paginator
                first={first}
                rows={pageSize}
                totalRecords={totalTestPlans}
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
