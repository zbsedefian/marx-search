import React, { useContext } from "react";
import { Link } from "react-router-dom";
import { WorkContext } from "../work/WorkContext";

export default function WorksList() {
  const { works, setCurrentWorkId } = useContext(WorkContext);

  return (
    <div className="bg-gray-50 dark:bg-gray-900 min-h-screen py-10 px-4 text-gray-800 dark:text-gray-200 font-serif">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-4xl font-semibold mb-10 text-center">Available Texts</h1>
        <ul className="space-y-6">
          {works.map((work) => (
            <li key={work.id} className="bg-white dark:bg-gray-800 shadow rounded-md p-4">
              <Link
                to={`/works/${work.id}`}
                onClick={() => setCurrentWorkId(work.id)}
                className="text-2xl text-blue-700 dark:text-blue-400 hover:underline font-medium"
              >
                {work.title}
              </Link>
              {work.author && (
                <span className="ml-2 text-gray-600 dark:text-gray-400">{work.author}</span>
              )}
              {work.description && (
                <p className="mt-2 text-gray-700 dark:text-gray-300 text-sm">{work.description}</p>
              )}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
