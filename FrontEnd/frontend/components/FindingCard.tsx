"use client";

import { useState } from "react";

interface FindingCardProps {
  title: string;
  severity: "High" | "Medium" | "Low";
  description: string;
  functionName: string;
  originalCode: string;
  patchedCode: string;
}

export default function FindingCard({
  title,
  severity,
  description,
  functionName,
  originalCode,
  patchedCode,
}: FindingCardProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="rounded-2xl border border-neutral-800 bg-neutral-900 overflow-hidden">

      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        className="w-full px-6 py-5 text-left"
      >
        <div className="flex items-center justify-between">

          <div>
            <span className="text-red-400 text-sm font-medium">
              {severity}
            </span>

            <h3 className="mt-1 text-lg font-semibold text-white">
              {title}
            </h3>

            <p className="mt-1 text-sm text-neutral-500">
              Function: {functionName}
            </p>
          </div>

          <span className="text-neutral-400 text-xl">
            {expanded ? "−" : "+"}
          </span>

        </div>
      </button>

      {expanded && (
        <div className="border-t border-neutral-800 p-6">

          <h4 className="text-sm font-medium text-neutral-400 mb-2">
            Explanation
          </h4>

          <p className="text-sm text-neutral-300 leading-6">
            {description}
          </p>

          <div className="mt-6">
            <h4 className="text-sm font-medium text-neutral-400 mb-2">
              Original Code
            </h4>

            <pre className="bg-black rounded-lg p-4 overflow-x-auto text-sm text-neutral-300">
              {originalCode}
            </pre>
          </div>

          <div className="mt-6">
            <h4 className="text-sm font-medium text-neutral-400 mb-2">
              Patched Code
            </h4>

            <pre className="bg-black rounded-lg p-4 overflow-x-auto text-sm text-neutral-300">
              {patchedCode}
            </pre>
          </div>

        </div>
      )}
    </div>
  );
}