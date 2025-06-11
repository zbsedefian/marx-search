import React, { useEffect, useState, useContext } from "react";
import { useParams, useSearchParams, Link } from "react-router-dom";
import DarkModeToggleFloating from "../darkmode/DarkModeToggleFloating";
import PassageSnippet from "../components/PassageSnippet";
import Pagination from "../components/Pagination";
import { WorkContext } from "../work/WorkContext";
import API_BASE_URL from "../config";

export default function TermDetail() {
  const { termId } = useParams();
  const [term, setTerm] = useState(null);
  const [passages, setPassages] = useState([]);
  const [total, setTotal] = useState(0);

  const [searchParams, setSearchParams] = useSearchParams();
  const page = parseInt(searchParams.get("page")) || 1;
  const pageSize = parseInt(searchParams.get("pageSize")) || 10;
  const { currentWorkId } = useContext(WorkContext);

  useEffect(() => {
    fetch(`${API_BASE_URL}/terms/${termId}`)
      .then((res) => res.json())
      .then(setTerm);

    const countUrl = new URL(
      `/terms/${termId}/passage_count`,
      API_BASE_URL
    );
    const passagesUrl = new URL(
      `/terms/${termId}/passages`,
      API_BASE_URL
    );
    passagesUrl.searchParams.set("page", page);
    passagesUrl.searchParams.set("page_size", pageSize);
    if (currentWorkId) {
      countUrl.searchParams.set("work_id", currentWorkId);
      passagesUrl.searchParams.set("work_id", currentWorkId);
    }
    fetch(countUrl)
      .then((res) => res.json())
      .then((data) => setTotal(data.count));

    fetch(passagesUrl)
      .then((res) => res.json())
      .then(setPassages);
  }, [termId, page, pageSize, currentWorkId]);

  // Try to extract the first passage's chapter number and work id
  const chapterFromFirstPassage = passages.length ? passages[0].chapter : null;
  const workFromFirstPassage = passages.length ? passages[0].work_id : null;

  if (!term)
    return (
      <div className="p-4 text-gray-700 dark:text-gray-300">
        Loading term...
      </div>
    );

  return (
    <div className="p-6 min-h-screen bg-[#fceedd] font-serif text-gray-800 dark:bg-[#1e1e1e] dark:text-gray-200">
      <h1 className="text-3xl font-bold mb-2">{term.term}</h1>
      <p className="text-md text-gray-700 dark:text-gray-300 mb-6">
        {term.definition}
      </p>

      <h2 className="text-xl font-semibold mb-2">Appears in:</h2>
      <ul className="space-y-4 list-none p-0">
        {" "}
        {passages.map((p) => (
          <PassageSnippet key={p.id} passage={p} term={term.term} workid={p.work_id} />
        ))}
      </ul>

      <Pagination
        page={page}
        total={total}
        pageSize={pageSize}
        setSearchParams={setSearchParams}
      />

      {/* Floating Back to Chapter */}
      {chapterFromFirstPassage && (
        <Link
          to={`/read/${workFromFirstPassage}/${chapterFromFirstPassage}`}
          className="fixed bottom-6 left-6 bg-blue-600 text-white px-4 py-2 rounded shadow-lg hover:bg-blue-700"
        >
          ← Back to Chapter {chapterFromFirstPassage}
        </Link>
      )}

      {/* Floating Dark Mode Toggle */}
      <DarkModeToggleFloating />
    </div>
  );
}
