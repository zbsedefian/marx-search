import React, { useContext } from "react";
import { Link } from "react-router-dom";
import { WorkContext } from "../work/WorkContext";

export default function WorksList() {
  const { works, setCurrentWorkId } = useContext(WorkContext);

  return (
    <div className="min-h-screen bg-[#fceedd] dark:bg-[#1b1b1b] text-gray-900 dark:text-gray-100 px-6 py-10 font-serif leading-relaxed">
      <div className="max-w-4xl mx-auto">
        {/* Intro Section with Logo and Description */}
        <div className="mb-16 text-center">
          <img
            src="/image/marxsearch-transparant.png"
            alt="Marx Search Logo"
            className="mx-auto h-20 mb-4"
          />
          <h2 className="text-2xl font-bold mb-2">Welcome to Marx Search</h2>
          <p className="text-md text-gray-700 dark:text-gray-300 max-w-2xl mx-auto">
            This site allows you to search across the works
            of Karl Marx and Friedrich Engels. Whether you're researching
            specific terms, exploring their ideas, or tracing concepts across
            volumes,
            <strong> Marx Search </strong> helps you quickly locate relevant
            passages.
          </p>
        </div>

        {/* Main Header */}
        <header className="mb-12 border-b border-gray-300 dark:border-gray-700 pb-4">
          <h1 className="text-4xl font-bold tracking-tight text-center">
            Available Texts
          </h1>
          <p className="mt-2 text-center text-sm text-gray-600 dark:text-gray-400 italic">
            Browse the collected works and select a volume to begin reading.
          </p>
        </header>

        {/* Works List */}
        <ul className="space-y-8">
          {works.map((work) => (
            <li
              key={work.id}
              className="p-6 border border-gray-300 dark:border-gray-700 rounded-lg bg-[#f7f1e9] dark:bg-[#252525] transition-shadow hover:shadow-md"
            >
              <Link
                to={`/works/${work.id}`}
                onClick={() => setCurrentWorkId(work.id)}
                className="text-2xl font-semibold text-blue-800 dark:text-blue-300 hover:underline"
              >
                {work.title}
              </Link>

              {work.author && (
                <div className="mt-1 text-gray-700 dark:text-gray-400 italic text-sm">
                  by {work.author}
                </div>
              )}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
