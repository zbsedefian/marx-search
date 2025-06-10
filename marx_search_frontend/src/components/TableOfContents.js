import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";

export default function TableOfContents({ workId }) {
  const [chapters, setChapters] = useState([]);

  useEffect(() => {
    const url = new URL("http://localhost:8000/chapters_with_sections");
    if (workId) {
      url.searchParams.set("work_id", workId);
    }
    fetch(url)
      .then((res) => res.json())
      .then(setChapters);
  }, [workId]);

  const grouped = chapters.reduce((acc, ch) => {
    const key = ch.part ? ch.part.number : "nopart";
    if (!acc[key]) {
      acc[key] = { part: ch.part, chapters: [] };
    }
    acc[key].chapters.push(ch);
    return acc;
  }, {});

  return (
    <div>
      {Object.values(grouped).map((group, idx) => (
        <div
          key={group.part ? group.part.number : `no-part-${idx}`}
          className="mb-10"
        >
          {group.part && (
            <h2 className="text-2xl font-semibold mb-3">
              Part {group.part.number}: {group.part.title}
            </h2>
          )}
          <ul className="space-y-6 ml-4">
            {group.chapters.map((ch) => (
              <li key={ch.number}>
                <Link
                  to={`/read/${workId || 1}/${ch.number}`}
                  className="text-xl text-blue-700 dark:text-blue-400 hover:underline font-medium"
                >
                  Chapter {ch.number}: {ch.title}
                </Link>
                {ch.sections.length > 0 && (
                  <ul className="ml-6 mt-2 space-y-1 text-sm text-gray-700 dark:text-gray-300">
                    {ch.sections.map((sec) => (
                      <li key={sec.section}>
                        <Link
                          to={`/read/${workId || 1}/${ch.number}#section-${sec.section}`}
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
