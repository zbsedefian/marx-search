import React, { useEffect, useState, useContext } from "react";
import { useParams, useSearchParams, Link } from "react-router-dom";
import DarkModeToggleFloating from "../darkmode/DarkModeToggleFloating";
import { WorkContext } from "../work/WorkContext";
import API_BASE_URL from "../config";

export default function Reader() {
  const { workId, chapterNumber } = useParams();
  const [searchParams] = useSearchParams();
  const highlightId = searchParams.get("highlight");

  const [chapterTitle, setChapterTitle] = useState("");
  const [part, setPart] = useState(null);
  const [passages, setPassages] = useState([]);
  const [sectionsMeta, setSectionsMeta] = useState([]);
  const [terms, setTerms] = useState([]);
  const [prevChapter, setPrevChapter] = useState(null);
  const [nextChapter, setNextChapter] = useState(null);
  const [allChapters, setAllChapters] = useState([]);
  const [showChapterMenu, setShowChapterMenu] = useState(false);
  const { works, currentWorkId, setCurrentWorkId } = useContext(WorkContext);
  const currentWorkTitle = works.find(
    (item) => item.id === currentWorkId
  )?.title;

  useEffect(() => {
    setCurrentWorkId(parseInt(workId, 10));
    const chapterUrl = new URL(
      `/chapter_data/${workId}/${parseInt(chapterNumber, 10)}`,
      API_BASE_URL
    );
    fetch(chapterUrl)
      .then((res) => res.json())
      .then((data) => {
        setPassages(data.passages);
        setSectionsMeta(data.sections);
        setTerms(data.terms);
        setChapterTitle(data.title);
        setPart(data.part);
        setPrevChapter(data.prev_chapter);
        setNextChapter(data.next_chapter);
      });
    const chaptersUrl = new URL("/chapters/", API_BASE_URL);
    chaptersUrl.searchParams.set("work_id", workId);
    fetch(chaptersUrl)
      .then((res) => res.json())
      .then(setAllChapters);
  }, [workId, chapterNumber]);

  useEffect(() => {
    if (highlightId) {
      const el = document.getElementById(highlightId);
      if (el) {
        setTimeout(() => {
          el.scrollIntoView({ behavior: "smooth", block: "center" });
          el.classList.add("bg-yellow-200");
          setTimeout(() => el.classList.remove("bg-yellow-200"), 2000);
        }, 100);
      }
    }
  }, [passages, highlightId]);

  const renderSuperscripts = (text) => {
    return text.replace(
      /(?<!\w)\.(\d+)(?!\w)/g,
      (_, num) => `<sup>${num}</sup>`
    );
  };

  const linkifyTerms = (text, terms) => {
    const sortedTerms = [...terms]
      .flatMap((t) => {
        const aliasList = [
          t.term,
          ...(t.aliases ? t.aliases.split(",").map((a) => a.trim()) : []),
        ];
        return aliasList.map((alias) => ({ alias, id: t.id }));
      })
      .sort((a, b) => b.alias.length - a.alias.length); // longest first

    let placeholderIndex = 0;
    const placeholders = {};
    let modifiedText = text;

    sortedTerms.forEach(({ alias, id }) => {
      const regex = new RegExp(
        `\\b${alias.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\b`,
        "gi"
      );
      modifiedText = modifiedText.replace(regex, (match) => {
        const key = `__TERM_PLACEHOLDER_${placeholderIndex++}__`;
        placeholders[key] = (
          <Link
            key={key}
            to={`/terms/${id}`}
            className="hover:underline hover:text-blue-600 cursor-pointer"
          >
            {match}
          </Link>
        );
        return key;
      });
    });

    return modifiedText
      .split(/(__TERM_PLACEHOLDER_\d+__)/g)
      .map((part) => placeholders[part] || part);
  };

  const sectionTitleFor = (section) => {
    const meta = sectionsMeta.find((s) => s.section === parseInt(section));
    return meta?.title || "";
  };

  const sections = [
    ...new Set(
      passages.map((p) =>
        p.section === null || p.section === -1 ? "none" : p.section
      )
    ),
  ];
  const hasNamedSections = sections.some((s) => s !== "none");

  return (
    <div className="min-h-screen flex gap-6 p-6 font-serif bg-[#fceedd] text-black dark:bg-[#1e1e1e] dark:text-gray-100 transition-colors duration-300">
      {/* Sidebar */}
      <aside className="hidden md:block w-56 sticky top-6 h-fit bg-[#fff9f3] dark:bg-[#2a2a2a] border dark:border-gray-700 p-4 rounded shadow text-sm">
        {hasNamedSections ? (
          <>
            <h2 className="font-semibold mb-2 text-gray-800 dark:text-gray-200">
              Sections
            </h2>
            <ul className="space-y-1">
              {sections.map((sec) => (
                <li key={sec}>
                  <a
                    href={`#section-${sec}`}
                    className="text-blue-600 hover:underline"
                  >
                    {sec === "none"
                      ? ""
                      : `Section ${sec}${
                          sectionTitleFor(sec)
                            ? ": " + sectionTitleFor(sec)
                            : ""
                        }`}
                  </a>
                </li>
              ))}
            </ul>
          </>
        ) : (
          <div className="text-gray-400 italic">No sections</div> // Optional filler or leave blank
        )}
      </aside>

      {/* Main content */}
      <div className="flex-1 space-y-5">
        {workId && (
          <div className="text-sm text-gray-600 dark:text-gray-400 uppercase tracking-wide">
            {currentWorkTitle}
          </div>
        )}
        {part && (
          <div className="text-sm text-gray-600 dark:text-gray-400 uppercase tracking-wide">
            Part {part.number}: {part.title}
          </div>
        )}

        <div className="flex justify-between items-center flex-wrap gap-3 mb-3">
          <h1 className="text-3xl font-bold">{chapterTitle}</h1>
          <div className="flex gap-4 text-sm flex-wrap">
            {prevChapter && (
              <Link
                to={`/read/${prevChapter.work_id}/${prevChapter.chapter_number}`}
                className="text-blue-600 hover:underline"
              >
                ← {prevChapter.title}
              </Link>
            )}
            {nextChapter && (
              <Link
                to={`/read/${nextChapter.work_id}/${nextChapter.chapter_number}`}
                className="text-blue-600 hover:underline"
              >
                {nextChapter.title} →
              </Link>
            )}
          </div>
        </div>

        {passages.map((p, i) => {
          const currentSection =
            p.section === null || p.section === -1 ? "none" : p.section;
          const prevSection = i > 0 ? passages[i - 1].section ?? "none" : null;

          return (
            <div key={p.id} id={p.id} className="leading-relaxed text-lg">
              {(i === 0 || currentSection !== prevSection) && (
                <div
                  id={`section-${currentSection}`}
                  className="scroll-mt-20 text-xl font-semibold mt-8 mb-2"
                >
                  {currentSection === "none" && hasNamedSections
                    ? ""
                    : currentSection !== "none"
                    ? `Section ${currentSection}${
                        sectionTitleFor(currentSection)
                          ? ": " + sectionTitleFor(currentSection)
                          : ""
                      }`
                    : null}
                </div>
              )}
              <div>{linkifyTerms(p.text, terms)}</div>
            </div>
          );
        })}

        {/* Bottom navigation */}
        <div className="flex justify-between items-center border-t pt-4 mt-8 text-sm">
          {prevChapter ? (
            <Link
              to={`/read/${prevChapter.work_id}/${prevChapter.chapter_number}`}
              className="text-blue-600 hover:underline"
            >
              ← {prevChapter.title}
            </Link>
          ) : (
            <div />
          )}
          {nextChapter && (
            <Link
              to={`/read/${nextChapter.work_id}/${nextChapter.chapter_number}`}
              className="text-blue-600 hover:underline"
            >
              {nextChapter.title} →
            </Link>
          )}
        </div>
      </div>

      {/* Floating chapter selector */}
      <div className="fixed bottom-6 left-6 flex flex-col-2 gap-2 z-50">
        <button
          className="bg-blue-600 text-white px-4 py-2 rounded-full shadow-lg hover:bg-blue-700 z-50"
          onClick={() => setShowChapterMenu(!showChapterMenu)}
        >
          Chapters
        </button>

        <button
          onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
          className="bg-gray-600 text-white px-4 py-2 rounded-full shadow-lg hover:bg-gray-700 z-50"
        >
          ↑ Top
        </button>
      </div>

      {showChapterMenu && (
        <div className="fixed bottom-20 left-6 w-72 max-h-[60vh] overflow-auto bg-white dark:bg-[#2a2a2a] border border-gray-300 dark:border-gray-700 rounded-lg shadow-xl p-4 z-50 text-sm">
          <h3 className="font-semibold mb-2 text-gray-800 dark:text-gray-100">
            Jump to Chapter
          </h3>
          <ul className="space-y-1">
            {allChapters.map((ch) => (
              <li key={ch.id}>
                <Link
                  to={`/read/${workId}/${ch.chapter_number}`}
                  className="text-blue-600 hover:underline"
                  onClick={() => setShowChapterMenu(false)}
                >
                  {ch.title}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      )}

      <DarkModeToggleFloating />
    </div>
  );
}
