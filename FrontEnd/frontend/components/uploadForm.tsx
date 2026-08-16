"use client";

import { useState } from "react";

export default function UploadForm({ onSubmit }: { onSubmit: (code: string, filename: string) => void }) {
  const [code, setCode] = useState("");
  const [filename, setFilename] = useState("Untitled.sol");

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith(".sol")) {
      alert("Please upload a .sol file");
      return;
    }

    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target?.result as string;
      setCode(text);
      setFilename(file.name);
    };
    reader.readAsText(file);
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-3">
        <label className="cursor-pointer bg-gray-800 hover:bg-gray-700 text-sm px-3 py-2 rounded-md">
          Upload .sol file
          <input
            type="file"
            accept=".sol"
            onChange={handleFileUpload}
            className="hidden"
          />
        </label>
        <span className="text-xs text-gray-500">{filename}</span>
      </div>

      <textarea
        value={code}
        onChange={(e) => setCode(e.target.value)}
        placeholder="Or paste your Solidity contract here..."
        className="w-full h-64 bg-gray-900 border border-gray-700 rounded-md p-3 font-mono text-sm"
      />

      <button
        onClick={() => onSubmit(code, filename)}
        disabled={!code.trim()}
        className="bg-blue-600 hover:bg-blue-500 disabled:opacity-40 text-white px-4 py-2 rounded-md text-sm"
      >
        Run Audit
      </button>
    </div>
  );
}