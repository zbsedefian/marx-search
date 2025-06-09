import React, { useContext } from "react";
import { Link } from "react-router-dom";
import { WorkContext } from "../work/WorkContext";

export default function WorksList() {
  const { works, setCurrentWorkId } = useContext(WorkContext);

  return (
    <div className="p-6 bg-[#fceedd] dark:bg-[#1e1e1e] min-h-screen text-gray-800 dark:text-gray-200 font-serif">
      <h1 className="text-3xl font-bold mb-8">Available Texts</h1>
      <ul className="space-y-6">
        {works.map((work) => (
          <li key={work.id}>
            <Link
              to={`/works/${work.id}`}
              onClick={() => setCurrentWorkId(work.id)}
              className="text-xl text-blue-700 dark:text-blue-400 hover:underline font-medium"
            >
              {work.title}
            </Link>
            {work.author && (
              <span className="ml-2 text-gray-600 dark:text-gray-400">{work.author}</span>
            )}
            {work.description && (
              <p className="ml-4 text-gray-700 dark:text-gray-300 text-sm">{work.description}</p>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
