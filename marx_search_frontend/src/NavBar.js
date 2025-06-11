import React, { useState, useContext } from "react";
import { Link, useNavigate } from "react-router-dom";
import DarkModeToggleFloating from "./darkmode/DarkModeToggleFloating";
import { WorkContext } from "./work/WorkContext";

export default function Navbar() {
  const [query, setQuery] = useState("");
  const [exactMatch, setExactMatch] = useState(false);
  const navigate = useNavigate();
  const { works, currentWorkId, setCurrentWorkId } = useContext(WorkContext);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      const searchParams = new URLSearchParams();
      searchParams.set("q", query.trim());
      if (exactMatch) {
        searchParams.set("exact", "true");
      }
      navigate({
        pathname: "/search",
        search: `?${searchParams.toString()}`,
      });
      setQuery("");
    }
  };

  return (
    <nav className="flex items-center justify-between p-4 bg-[#fceedd] dark:bg-[#1e1e1e] shadow font-serif flex-wrap">
      {/* Logo / Title */}
      <Link to="/" className="mr-4">
        <img
          src="/image/marxsearch-transparant.png"
          alt="Marx Search Logo"
          className="h-10 w-auto"
        />
      </Link>

      {/* Navigation Links and Search */}
      <div className="flex items-center gap-4 flex-wrap">
        <Link
          to={currentWorkId ? `/read/${currentWorkId}/1` : "/read/1/1"}
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
        <select
          value={currentWorkId || ""}
          onChange={(e) =>
            setCurrentWorkId(e.target.value ? parseInt(e.target.value) : null)
          }
          className="px-2 py-1 border rounded dark:bg-[#1e1e1e] dark:text-white dark:border-gray-600"
        >
          <option value="">All Works</option>
          {works.map((w) => (
            <option key={w.id} value={w.id}>
              {w.title}
            </option>
          ))}
        </select>

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
