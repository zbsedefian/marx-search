import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";

export default function Home() {
  const [parts, setParts] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8000/parts_with_chapters_sections")
      .then((res) => res.json())
      .then(setParts);
  }, []);

  return (
    <div className="p-6 bg-[#fceedd] dark:bg-[#1e1e1e] min-h-screen text-gray-800 dark:text-gray-200 font-serif">
      <h1 className="text-3xl font-bold mb-8">Capital Volume 1</h1>

      {parts.map((part) => (
        <div key={part.number} className="mb-10">
          <h2 className="text-2xl font-semibold mb-3">
            Part {part.number}: {part.title}
          </h2>

          <ul className="space-y-6 ml-4">
            {part.chapters.map((ch) => (
              <li key={ch.id}>
                <Link
                  to={`/read/${ch.id}`}
                  className="text-xl text-blue-700 dark:text-blue-400 hover:underline font-medium"
                >
                  Chapter {ch.id}: {ch.title}
                </Link>
                {ch.sections.length > 0 && (
                  <ul className="ml-6 mt-2 space-y-1 text-sm text-gray-700 dark:text-gray-300">
                    {ch.sections.map((sec) => (
                      <li key={sec.section}>
                        <Link
                          to={`/read/${ch.id}#section-${sec.section}`}
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
