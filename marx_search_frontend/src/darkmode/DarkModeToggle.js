import { useContext } from "react";
import { DarkModeContext } from "./DarkModeContext";

export default function DarkModeToggle() {
  const { darkMode, setDarkMode } = useContext(DarkModeContext);
  return (
    <button
      onClick={() => setDarkMode(!darkMode)}
      className="p-2 rounded bg-gray-200 dark:bg-gray-700"
    >
      {darkMode ? "🌙 Dark" : "☀️ Light"}
    </button>
  );
}
