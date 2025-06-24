import React from 'react';
import PropTypes from 'prop-types';

const AdminTable = ({
  columns = [],
  data = [],
  onSort,
  onRowClick,
  bulkActions = [],
  loading = false,
  emptyMessage = 'No data available',
  selectedRows = [],
  onSelectRow,
  onSelectAll
}) => {
  const hasBulkActions = bulkActions.length > 0;
  const allSelected = selectedRows.length === data.length && data.length > 0;

  const handleSort = (column) => {
    if (column.sortable && onSort) {
      onSort(column.key);
    }
  };

  const handleRowClick = (row, index) => {
    if (onRowClick) {
      onRowClick(row, index);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-600"></div>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500 dark:text-gray-400">
        {emptyMessage}
      </div>
    );
  }

  return (
    <div className="overflow-x-auto shadow-md rounded-lg">
      <table className="min-w-full bg-white dark:bg-gray-800">
        <thead className="bg-gray-50 dark:bg-gray-900">
          <tr>
            {hasBulkActions && (
              <th className="px-6 py-3 text-left">
                <input
                  type="checkbox"
                  checked={allSelected}
                  onChange={(e) => onSelectAll && onSelectAll(e.target.checked)}
                  className="rounded border-gray-300 dark:border-gray-600 text-orange-600 focus:ring-orange-500"
                />
              </th>
            )}
            {columns.map((column) => (
              <th
                key={column.key}
                className={`px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider ${
                  column.sortable ? 'cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800' : ''
                }`}
                onClick={() => handleSort(column)}
              >
                <div className="flex items-center">
                  {column.label}
                  {column.sortable && (
                    <svg
                      className="w-4 h-4 ml-1"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
                        clipRule="evenodd"
                      />
                    </svg>
                  )}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
          {data.map((row, rowIndex) => (
            <tr
              key={rowIndex}
              className={`${
                onRowClick ? 'cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700' : ''
              } ${selectedRows.includes(rowIndex) ? 'bg-blue-50 dark:bg-blue-900/20' : ''}`}
              onClick={() => handleRowClick(row, rowIndex)}
            >
              {hasBulkActions && (
                <td className="px-6 py-4 whitespace-nowrap">
                  <input
                    type="checkbox"
                    checked={selectedRows.includes(rowIndex)}
                    onChange={(e) => {
                      e.stopPropagation();
                      onSelectRow && onSelectRow(rowIndex);
                    }}
                    onClick={(e) => e.stopPropagation()}
                    className="rounded border-gray-300 dark:border-gray-600 text-orange-600 focus:ring-orange-500"
                  />
                </td>
              )}
              {columns.map((column) => (
                <td
                  key={column.key}
                  className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100"
                >
                  {column.render
                    ? column.render(row[column.key], row, rowIndex)
                    : row[column.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

AdminTable.propTypes = {
  columns: PropTypes.arrayOf(
    PropTypes.shape({
      key: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
      sortable: PropTypes.bool,
      render: PropTypes.func
    })
  ).isRequired,
  data: PropTypes.array.isRequired,
  onSort: PropTypes.func,
  onRowClick: PropTypes.func,
  bulkActions: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string.isRequired,
      action: PropTypes.func.isRequired
    })
  ),
  loading: PropTypes.bool,
  emptyMessage: PropTypes.string,
  selectedRows: PropTypes.array,
  onSelectRow: PropTypes.func,
  onSelectAll: PropTypes.func
};

export default AdminTable;