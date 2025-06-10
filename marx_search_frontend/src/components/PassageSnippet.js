import React, { useContext } from "react";
import { Link } from "react-router-dom";
import { WorkContext } from "../work/WorkContext";

export default function PassageSnippet({ passage, term }) {
  const { works } = useContext(WorkContext);
  const work = works.find((w) => w.id === passage.work_id);
  const highlightTermInText = (text, term) => {
    if (!term) return text;
    const regex = new RegExp(`(${term})`, "gi");
    return text.split(regex).map((part, i) =>
      regex.test(part) ? (
        <mark key={i} className="bg-yellow-200">
          {part}
        </mark>
      ) : (
        part
      )
    );
  };

  const truncateText = (text, maxLength = 300) => {
    if (!text) return "";
    return text.length > maxLength ? text.slice(0, maxLength) + "…" : text;
  };

  return (
    <li
      key={passage.id}
      className="list-none mb-6 p-5 max-w-3xl mx-auto rounded border bg-[#fff8f0] dark:bg-[#2a2a2a] dark:border-gray-700 shadow"
    >
      {/* Chapter title and work name */}
      <div className="flex justify-between items-baseline mb-1 text-md font-semibold">
        <Link
          to={`/read/${passage.work_id}/${passage.chapter}`}
          className="text-blue-600 hover:underline"
        >
          Chapter {passage.chapter}: {passage.chapter_title}
        </Link>
        {work && (
          <span className="italic text-sm text-gray-600 dark:text-gray-400">
            {work.title}
          </span>
        )}
      </div>

      {/* Section title (optional) */}
      {passage.section_title && (
        <div className="text-sm text-gray-600 dark:text-gray-400 italic mb-1">
          Section {passage.section}: {passage.section_title}
        </div>
      )}

      {/* Paragraph link */}
      <div className="text-sm mb-3">
        <Link
          to={`/read/${passage.work_id}/${passage.chapter}?highlight=${passage.id}`}
          className="text-blue-600 hover:underline"
        >
          Paragraph {passage.paragraph}
        </Link>
      </div>

      {/* Snippet */}
      <blockquote className="text-sm text-gray-700 dark:text-gray-300 border-l-4 border-yellow-300 pl-4 italic">
        {highlightTermInText(
          truncateText(passage.text_snippet || passage.text),
          term
        )}
      </blockquote>
    </li>
  );
}
