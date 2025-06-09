import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";

export default function TableOfContents({ workId }) {
  const [parts, setParts] = useState([]);

  useEffect(() => {
    const url = new URL("http://localhost:8000/parts_with_chapters_sections");
    if (workId) {
      url.searchParams.set("work_id", workId);
    }
    fetch(url)
      .then((res) => res.json())
      .then(setParts);
  }, [workId]);

  return (
    <div>
      {parts.map((part) => (
        <div key={part.number} className="mb-10">
          <h2 className="text-2xl font-semibold mb-3">
            Part {part.number}: {part.title}
          </h2>
          <ul className="space-y-6 ml-4">
            {part.chapters.map((ch) => (
              <li key={ch.id}>
                <Link
                  to={`/read/${currentWorkId || 1}/${ch.id}`}
                  className="text-xl text-blue-700 dark:text-blue-400 hover:underline font-medium"
                >
                  Chapter {ch.id}: {ch.title}
                </Link>
                {ch.sections.length > 0 && (
                  <ul className="ml-6 mt-2 space-y-1 text-sm text-gray-700 dark:text-gray-300">
                    {ch.sections.map((sec) => (
                      <li key={sec.section}>
                        <Link
                          to={`/read/${currentWorkId || 1}/${ch.id}#section-${sec.section}`}
                          className="hover:underline"
                        >
                          Section {sec.section}: {sec.title}
                        </Link>
                      </li>
                    ))}
                  </ul>
                )}
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
