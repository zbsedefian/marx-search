import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import DarkModeToggleFloating from "./darkmode/DarkModeToggleFloating";

export default function Navbar() {
  const [query, setQuery] = useState("");
  const [exactMatch, setExactMatch] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      const encodedQuery = encodeURIComponent(query.trim());
      const searchParams = new URLSearchParams();
      searchParams.set("q", encodedQuery);
      if (exactMatch) {
        searchParams.set("exact", "true");
      }
      navigate(`/search?${searchParams.toString()}`);
      setQuery("");
    }
  };

  return (
    <nav className="flex items-center justify-between p-4 bg-[#fceedd] dark:bg-[#1e1e1e] shadow font-serif flex-wrap">
      {/* Logo / Title */}
      <Link
        to="/"
        className="text-xl font-bold text-gray-800 dark:text-gray-100 mr-4"
      >
        Marx Search
      </Link>

      {/* Navigation Links and Search */}
      <div className="flex items-center gap-4 flex-wrap">
        <Link
          to="/read/1"
          className="text-blue-700 dark:text-blue-400 hover:underline"
        >
          Read
        </Link>
        <Link
          to="/terms"
          className="text-blue-700 dark:text-blue-400 hover:underline"
        >
          Glossary
        </Link>

        <form
          onSubmit={handleSubmit}
          className="flex items-center gap-2 flex-wrap"
        >
          <input
            type="text"
            placeholder="Search terms or text..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="px-3 py-1 rounded border border-gray-400 dark:border-gray-600 bg-white dark:bg-[#1e1e1e] text-gray-800 dark:text-white"
          />
          <label className="flex items-center text-sm gap-1 text-gray-800 dark:text-white">
            <input
              type="checkbox"
              checked={exactMatch}
              onChange={() => setExactMatch(!exactMatch)}
            />
            Exact Match
          </label>
          <button
            type="submit"
            className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Search
          </button>
        </form>
      </div>

      <DarkModeToggleFloating />
    </nav>
  );
}
