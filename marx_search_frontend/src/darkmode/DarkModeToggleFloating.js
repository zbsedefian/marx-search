import { useContext } from "react";
import { DarkModeContext } from "./DarkModeContext"; // adjust path as needed

export default function DarkModeToggleFloating() {
  const { darkMode, setDarkMode } = useContext(DarkModeContext);

  return (
    <button
      onClick={() => setDarkMode(!darkMode)}
      className="fixed bottom-4 right-4 z-50 p-2 rounded-full bg-white dark:bg-gray-800 shadow-lg hover:scale-105 transition-transform"
      aria-label="Toggle Dark Mode"
    >
      {darkMode ? "☀️" : "🌙"}
    </button>
  );
}
