import React, { createContext, useEffect, useState } from "react";

export const WorkContext = createContext();

export const WorkProvider = ({ children }) => {
  const [works, setWorks] = useState([]);
  const [currentWorkId, setCurrentWorkId] = useState(() => {
    const saved = localStorage.getItem("currentWorkId");
    return saved ? parseInt(saved) : null;
  });

  useEffect(() => {
    fetch("http://localhost:8000/works/")
      .then((res) => res.json())
      .then(setWorks);
  }, []);

  useEffect(() => {
    if (currentWorkId !== null) {
      localStorage.setItem("currentWorkId", currentWorkId);
    }
  }, [currentWorkId]);

  return (
    <WorkContext.Provider value={{ works, currentWorkId, setCurrentWorkId }}>
      {children}
    </WorkContext.Provider>
  );
};
