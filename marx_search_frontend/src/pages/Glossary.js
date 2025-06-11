import React, { useEffect, useState, useContext } from "react";
import { Link } from "react-router-dom";
import { WorkContext } from "../work/WorkContext";
import API_BASE_URL from "../config";

export default function Glossary() {
  const [terms, setTerms] = useState([]);
  const [query, setQuery] = useState("");
  const { currentWorkId } = useContext(WorkContext);

  useEffect(() => {
    const url = new URL("/terms/", API_BASE_URL);
    // if (currentWorkId) {
    //   url.searchParams.set("work_id", currentWorkId);
    // }
    fetch(url)
      .then((res) => res.json())
      .then((data) => setTerms(data));
  }, [currentWorkId]);

  const filtered = terms.filter((t) =>
    t.term.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="p-6 min-h-screen bg-[#fceedd] font-serif text-gray-800 dark:bg-[#1e1e1e] dark:text-gray-200">
      <h1 className="text-3xl font-bold mb-4">Glossary</h1>

      <input
        type="text"
        placeholder="Search terms..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="w-full p-2 mb-6 rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-[#2a2a2a] text-gray-800 dark:text-gray-200"
      />

      <ul className="space-y-4">
        {filtered.map((term) => (
          <li
            key={term.id}
            className="p-4 bg-[#fff8f0] dark:bg-[#2a2a2a] rounded shadow"
          >
            <Link
              to={`/terms/${term.id}`}
              className="text-blue-600 hover:underline"
            >
              <div className="text-lg font-semibold">{term.term}</div>
            </Link>
            <div className="text-sm mt-1 text-gray-700 dark:text-gray-300">
              {term.definition}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
