import { useLocation, Link, useSearchParams } from "react-router-dom";
import React, { useEffect, useState, useContext } from "react";
import API_BASE_URL from "../config";
import PassageSnippet from "../components/PassageSnippet";
import Pagination from "../components/Pagination";
import { WorkContext } from "../work/WorkContext";

export default function SearchResults() {
  const query = new URLSearchParams(useLocation().search).get("q") || "";
  const [results, setResults] = useState(null);
  const [total, setTotal] = useState(0);

  const [searchParams, setSearchParams] = useSearchParams();
  const page = parseInt(searchParams.get("page")) || 1;
  const pageSize = parseInt(searchParams.get("pageSize")) || 10;
  const { currentWorkId } = useContext(WorkContext);

  useEffect(() => {
    if (query) {
      const params = new URLSearchParams();
      params.set("q", query);
      params.set("page", page);
      params.set("page_size", pageSize);
      if (currentWorkId) {
        params.set("work_id", currentWorkId);
      }
      fetch(`${API_BASE_URL}/search?${params.toString()}`)
        .then((res) => res.json())
        .then((data) => {
          setResults(data);
          setTotal(data.total_passages || 0);
        });
    }
  }, [query, page, pageSize, currentWorkId]);

  if (!results) {
    return <div className="p-6">Searching for “{query}”...</div>;
  }

  if (!query) {
    return <div className="p-6">Please enter a search query.</div>;
  }

  if (!results) {
    return <div className="p-6">Searching for “{query}”...</div>;
  }

  return (
    <div className="p-6 bg-[#fceedd] dark:bg-[#1e1e1e] min-h-screen text-gray-800 dark:text-gray-200 font-serif">
      <h1 className="text-2xl font-bold mb-4">Search Results for “{query}”</h1>

      {results?.terms?.length > 0 && (
        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Matching Terms</h2>
          <ul className="space-y-2">
            {results.terms.map((term) => (
              <li key={term.id}>
                <Link
                  to={`/terms/${term.id}`}
                  className="text-blue-600 dark:text-blue-400 hover:underline"
                >
                  {term.term}
                </Link>{" "}
                –{" "}
                <span className="text-gray-700 dark:text-gray-300">
                  {term.definition}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {results?.passages?.length > 0 && (
        <div>
          <ul className="space-y-4 list-none p-0">
            {" "}
            {results.passages.map((p) => (
              <PassageSnippet key={p.id} passage={p} term={query} />
            ))}
          </ul>
        </div>
      )}

      <Pagination
        page={page}
        total={total}
        pageSize={pageSize}
        setSearchParams={setSearchParams}
      />
      {results?.terms?.length === 0 && results?.passages?.length === 0 && (
        <p className="italic text-gray-600">No results found.</p>
      )}
    </div>
  );
}
