import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Reader from "./pages/Reader";
import Glossary from "./pages/Glossary";
import TermDetail from "./pages/TermDetail";
import WorksList from "./pages/WorksList";
import WorkTableOfContents from "./pages/WorkTableOfContents";
import NavBar from "./NavBar";
import Footer from "./Footer";
import SearchResults from "./pages/SearchResults";

export default function App() {
  return (
    <Router>
      <div className="flex flex-col min-h-screen">
        <NavBar />
        <div className="flex-grow">
          <Routes>
            <Route path="/" element={<WorksList />} />
            <Route path="/works/:workId" element={<WorkTableOfContents />} />
            <Route path="/read/:workId/:chapterNumber" element={<Reader />} />
            <Route path="/terms" element={<Glossary />} />
            <Route path="/terms/:termId" element={<TermDetail />} />
            <Route path="/search" element={<SearchResults />} />
            <Route path="*" element={<WorksList />} />
          </Routes>
        </div>
        <Footer />
      </div>
    </Router>
  );
}
