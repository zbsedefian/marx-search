import React from "react";

export default function Pagination({ page, total, pageSize, setSearchParams }) {
  const totalPages = Math.ceil(total / pageSize);

  if (totalPages <= 1) return null;

  const goToPage = (newPage) => {
    setSearchParams((prev) => {
      const params = new URLSearchParams(prev);
      params.set("page", newPage);
      params.set("pageSize", pageSize);
      return params;
    });
  };

  const changePageSize = (newSize) => {
    setSearchParams((prev) => {
      const params = new URLSearchParams(prev);
      params.set("page", 1);
      params.set("pageSize", newSize);
      return params;
    });
  };

  return (
    <div className="mt-6 flex justify-center items-center flex-wrap gap-4 text-sm">
      <button
        onClick={() => goToPage(page - 1)}
        disabled={page === 1}
        className="px-3 py-1 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-white rounded hover:bg-gray-300 dark:hover:bg-gray-600 disabled:opacity-50"
      >
        ← Previous
      </button>

      <span>
        Page <strong>{page}</strong> of <strong>{totalPages}</strong>
      </span>

      <button
        onClick={() => goToPage(page + 1)}
        disabled={page >= totalPages}
        className="px-3 py-1 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-white rounded hover:bg-gray-300 dark:hover:bg-gray-600 disabled:opacity-50"
      >
        Next →
      </button>

      <select
        value={pageSize}
        onChange={(e) => changePageSize(e.target.value)}
        className="ml-2 p-1 border rounded bg-white dark:bg-[#2a2a2a] dark:text-white dark:border-gray-600"
      >
        {[5, 10, 20, 50].map((size) => (
          <option key={size} value={size}>
            {size} / page
          </option>
        ))}
      </select>

      <select
        value={page}
        onChange={(e) => goToPage(e.target.value)}
        className="p-1 border rounded bg-white dark:bg-[#2a2a2a] dark:text-white dark:border-gray-600"
      >
        {Array.from({ length: totalPages }, (_, i) => (
          <option key={i + 1} value={i + 1}>
            Jump to page {i + 1}
          </option>
        ))}
      </select>
    </div>
  );
}
