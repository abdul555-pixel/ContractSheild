"use client";

import ReactDiffViewer from "react-diff-viewer-continued";

interface CodeDiffViewerProps {
  originalCode: string;
  patchedCode: string;
}

export default function CodeDiffViewer({
  originalCode,
  patchedCode,
}: CodeDiffViewerProps) {
  return (
    <div className="w-full overflow-hidden rounded-lg border border-neutral-700">
      <ReactDiffViewer
        oldValue={originalCode}
        newValue={patchedCode}
        splitView={true}
        leftTitle="Original Code"
        rightTitle="Patched Code"
      />
    </div>
  );
}