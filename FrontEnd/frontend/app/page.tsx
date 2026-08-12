"use client";

import Image from "next/image";
import { useRef, useState } from "react";
import CodeDiffViewer from "@/components/CodeDiffViewer";

type Assessment = {
  title: string;
  plain_explanation: string;
  impact: string;
  exploitability: string;
  exploitability_reason: string;
  suggested_fix: string;
  original_code: string;
  patched_code: string;
};

type FindingResult = {
  finding: {
    title: string;
    description: string;
    severity: string;
    function_name: string;
    line_numbers: number[];
  };

  assessment: Assessment;

  risk_score: number;
};

type AuditResponse = {
  risk_score: number;
  risk_level: string;
  findings: FindingResult[];
};

export default function Home() {
  const [contractCode, setContractCode] = useState("");
  const [fileName, setFileName] = useState("");

  const [auditResult, setAuditResult] =
    useState<AuditResponse | null>(null);

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  const fileInputRef = useRef<HTMLInputElement>(null);

  // ============================================================
  // FILE UPLOAD
  // ============================================================

  const handleFileUpload = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];

    if (!file) return;

    if (!file.name.endsWith(".sol")) {
      setError("Please upload a Solidity (.sol) file.");
      return;
    }

    setError("");

    setFileName(file.name);

    const reader = new FileReader();

    reader.onload = (e) => {
      const content = e.target?.result;

      if (typeof content === "string") {
        setContractCode(content);
      }
    };

    reader.readAsText(file);
  };

  // ============================================================
  // OPEN FILE PICKER
  // ============================================================

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  // ============================================================
  // ANALYZE CONTRACT
  // ============================================================

  const handleAnalyze = async () => {
    if (!contractCode.trim()) {
      setError("Please paste or upload a Solidity contract.");
      return;
    }

    setLoading(true);
    setError("");
    setAuditResult(null);

    try {
      const apiUrl =
        process.env.NEXT_PUBLIC_API_URL ||
        "http://127.0.0.1:8000";

      const response = await fetch(
        `${apiUrl}/audit/`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            contract: contractCode,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Audit failed."
        );
      }

      setAuditResult(data);

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong while analyzing the contract."
      );
    } finally {
      setLoading(false);
    }
  };

  // ============================================================
  // NEW SCAN
  // ============================================================

  const handleNewScan = () => {
    setContractCode("");
    setFileName("");
    setAuditResult(null);
    setError("");

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <main className="min-h-screen bg-[#0A0A0A] text-white flex flex-col">

      {/* ======================================================
          NAVBAR
      ====================================================== */}

      <header className="w-full border-b border-neutral-800 px-8 py-5 flex items-center justify-between">

        <div className="flex items-center">

          <div className="flex items-center justify-center">

            <Image
              src="/logo.png"
              alt="ContractShield Logo"
              width={52}
              height={52}
              priority
              className="select-none"
            />

          </div>

          <div>

            <h1 className="font-semibold text-lg">
              ContractShield
            </h1>

          </div>

        </div>

        <button
          onClick={handleNewScan}
          className="px-4 py-2 rounded-xl border border-neutral-700 hover:bg-neutral-800 transition"
        >
          New Scan
        </button>

      </header>


      {/* ======================================================
          HERO
      ====================================================== */}

      <section className="flex-1 flex items-center justify-center px-6 py-12">

        <div className="w-full max-w-4xl">

          {/* ==================================================
              TITLE
          ================================================== */}

          <div className="text-center mb-10">

            <h1 className="text-5xl font-bold tracking-tight">
              Analyze Smart Contracts
            </h1>

            <p className="mt-4 text-neutral-400 text-md max-w-2xl mx-auto">
              Paste your Solidity contract below and let AI detect
              vulnerabilities, explain risks, and recommend fixes before
              deployment.
            </p>

          </div>


          {/* ==================================================
              INPUT CARD
          ================================================== */}

          <div className="rounded-3xl border border-neutral-800 bg-neutral-900/70 backdrop-blur-xl overflow-hidden shadow-2xl">

            <textarea
              value={contractCode}
              onChange={(e) =>
                setContractCode(e.target.value)
              }
              placeholder="// Paste your Solidity smart contract here..."
              className="w-full h-[420px] bg-transparent resize-none outline-none p-8 text-neutral-200 placeholder:text-neutral-500 font-mono text-sm"
            />


            <div className="border-t border-neutral-800 px-6 py-4 flex justify-between items-center">

              {/* Hidden file input */}

              <input
                ref={fileInputRef}
                type="file"
                accept=".sol"
                onChange={handleFileUpload}
                className="hidden"
              />


              {/* Upload .sol */}

              <button
                onClick={handleUploadClick}
                className="text-sm text-neutral-400 hover:text-white transition"
              >
                📎 {fileName || "Upload .sol"}
              </button>


              {/* Analyze Contract */}

              <button
                onClick={handleAnalyze}
                disabled={loading}
                className="px-6 py-3 rounded-2xl bg-white text-black font-medium hover:scale-105 transition duration-200 disabled:opacity-50 disabled:hover:scale-100"
              >
                {loading
                  ? "Analyzing..."
                  : "Analyze Contract →"}
              </button>

            </div>

          </div>


          {/* ==================================================
              ERROR
          ================================================== */}

          {error && (

            <div className="mt-4 rounded-xl border border-red-900 bg-red-950/30 p-4 text-sm text-red-400">
              {error}
            </div>

          )}


          {/* ==================================================
              SECURITY REPORT
          ================================================== */}

          {auditResult && (

            <div className="mt-12">

              <h2 className="text-2xl font-semibold mb-6">
                Security Report
              </h2>


              {/* Risk Summary */}

              <div className="grid md:grid-cols-2 gap-4 mb-10">

                <div className="rounded-2xl border border-neutral-800 bg-neutral-900 p-6">

                  <p className="text-sm text-neutral-500">
                    Risk Level
                  </p>

                  <p className="mt-2 text-2xl font-semibold">
                    {auditResult.risk_level}
                  </p>

                </div>


                <div className="rounded-2xl border border-neutral-800 bg-neutral-900 p-6">

                  <p className="text-sm text-neutral-500">
                    Risk Score
                  </p>

                  <p className="mt-2 text-2xl font-semibold">
                    {auditResult.risk_score}/10
                  </p>

                </div>

              </div>


              {/* Findings */}

              {auditResult.findings.map(
                (item, index) => (

                  <div
                    key={index}
                    className="mb-12"
                  >

                    {/* Finding Header */}

                    <div className="mb-6">

                      <h3 className="text-xl font-semibold">
                        {item.assessment.title}
                      </h3>

                      <p className="mt-2 text-neutral-400">
                        {item.assessment.plain_explanation}
                      </p>

                    </div>


                    {/* Finding Details */}

                    <div className="grid md:grid-cols-3 gap-4 mb-6">

                      <div className="rounded-xl border border-neutral-800 bg-neutral-900 p-5">

                        <p className="text-sm text-neutral-500">
                          Severity
                        </p>

                        <p className="mt-1 font-medium">
                          {item.finding.severity}
                        </p>

                      </div>


                      <div className="rounded-xl border border-neutral-800 bg-neutral-900 p-5">

                        <p className="text-sm text-neutral-500">
                          Exploitability
                        </p>

                        <p className="mt-1 font-medium">
                          {item.assessment.exploitability}
                        </p>

                      </div>


                      <div className="rounded-xl border border-neutral-800 bg-neutral-900 p-5">

                        <p className="text-sm text-neutral-500">
                          Risk Score
                        </p>

                        <p className="mt-1 font-medium">
                          {item.risk_score}/10
                        </p>

                      </div>

                    </div>


                    {/* Impact */}

                    <div className="mb-6">

                      <h4 className="text-lg font-medium mb-2">
                        Impact
                      </h4>

                      <p className="text-neutral-400">
                        {item.assessment.impact}
                      </p>

                    </div>


                    {/* Suggested Fix */}

                    <div className="mb-6">

                      <h4 className="text-lg font-medium mb-2">
                        Suggested Fix
                      </h4>

                      <p className="text-neutral-400">
                        {item.assessment.suggested_fix}
                      </p>

                    </div>


                    {/* Code Diff */}

                    {item.assessment.original_code &&
                      item.assessment.patched_code && (

                        <div>

                          <h4 className="text-lg font-medium mb-4">
                            Code Changes
                          </h4>

                          <CodeDiffViewer
                            originalCode={
                              item.assessment.original_code
                            }
                            patchedCode={
                              item.assessment.patched_code
                            }
                          />

                        </div>

                      )}

                  </div>

                )
              )}

            </div>

          )}


          {/* ==================================================
              BOTTOM FEATURES
          ================================================== */}

          <div className="mt-8 flex justify-center gap-8 text-sm text-neutral-500 flex-wrap">

            <span>
              🔒 Reentrancy Detection
            </span>

            <span>
              ⚡ Gas Optimization
            </span>

            <span>
              🧠 AI Explanations
            </span>

            <span>
              📄 Security Report
            </span>

          </div>

        </div>

      </section>

    </main>
  );
}