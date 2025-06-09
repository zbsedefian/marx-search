import React, { useContext, useEffect } from "react";
import { useParams } from "react-router-dom";
import TableOfContents from "../components/TableOfContents";
import { WorkContext } from "../work/WorkContext";

export default function WorkTableOfContents() {
  const { workId } = useParams();
  const { setCurrentWorkId } = useContext(WorkContext);

  useEffect(() => {
    if (workId) {
      setCurrentWorkId(parseInt(workId, 10));
    }
  }, [workId, setCurrentWorkId]);

  return (
    <div className="p-6 bg-[#fceedd] dark:bg-[#1e1e1e] min-h-screen text-gray-800 dark:text-gray-200 font-serif">
      <TableOfContents workId={parseInt(workId, 10)} />
    </div>
  );
}
