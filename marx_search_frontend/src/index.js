import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";
import { DarkModeProvider } from "./darkmode/DarkModeContext";
import { WorkProvider } from "./work/WorkContext";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <DarkModeProvider>
      <WorkProvider>
        <App />
      </WorkProvider>
    </DarkModeProvider>
  </React.StrictMode>
);
