"use client";

import { useEffect, useState } from "react";

type ScanSummary = {
  id: number;
  contract_name: string | null;
  risk_level: string;
  risk_score: number | null;
  created_at: string;
};

export default function ScanHistorySidebar({
  onSelectScan,
  onNewScan,
  activeScanId,
  onScanDeleted,
  isOpen,
  refreshTrigger,
}: {
  onSelectScan: (id: number) => void;
  onNewScan: () => void;
  activeScanId?: number | null;
  onScanDeleted?: (id: number) => void;
  isOpen: boolean;
  refreshTrigger?: number;
}) {
  const [scans, setScans] = useState<ScanSummary[]>([]);
  const [loading, setLoading] = useState(true);

  const apiUrl =
    process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  const fetchScans = async () => {
    try {
      const res = await fetch(`${apiUrl}/scans/`);
      const data = await res.json();
      setScans(data);
    } catch (err) {
      console.error("Failed to load scan history:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchScans();
  }, [refreshTrigger]);

  const handleDelete = async (
    id: number,
    name: string,
    e: React.MouseEvent
  ) => {
    e.stopPropagation();

    const confirmed = window.confirm(
      `Delete "${name}"? This can't be undone.`
    );

    if (!confirmed) return;

    try {
      const res = await fetch(`${apiUrl}/scans/${id}`, {
        method: "DELETE",
      });

      if (!res.ok) {
        throw new Error("Delete request failed");
      }

      setScans((prev) => prev.filter((s) => s.id !== id));

      // If the deleted scan was the one currently open,
      // let the parent know so it can clear the main view.
      if (id === activeScanId && onScanDeleted) {
        onScanDeleted(id);
      }
    } catch (err) {
      console.error("Failed to delete scan:", err);
      alert("Failed to delete this scan. Please try again.");
    }
  };

  const severityDot = (level: string) => {
    if (level === "Critical") return "bg-red-500";
    if (level === "High") return "bg-orange-400";
    if (level === "Medium") return "bg-yellow-400";
    return "bg-green-500";
  };

  const timeAgo = (iso: string) => {
    const diffMs = Date.now() - new Date(iso).getTime();
    const mins = Math.floor(diffMs / 60000);
    if (mins < 1) return "Just now";
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    return `${Math.floor(hrs / 24)}d ago`;
  };

  return (
    <aside
      className={`w-64 h-screen fixed left-0 top-0 bg-[#0A0A0A] border-r border-neutral-800 flex flex-col z-20 transition-transform duration-300 ease-in-out ${
        isOpen ? "translate-x-0" : "-translate-x-full"
      }`}
    >
      {/* History label */}
      <div className="px-4 pt-4 pb-1 flex justify-center">
        <p className="text-xs font-medium text-neutral-500 tracking-wide">
          Recent Scans
        </p>
      </div>

      {/* Scrollable list */}
      <div className="flex-1 overflow-y-auto px-2 pb-4 space-y-0.5">
        {loading && (
          <p className="px-3 py-2 text-xs text-neutral-600">Loading…</p>
        )}

        {!loading && scans.length === 0 && (
          <p className="px-3 py-2 text-xs text-neutral-600">
            No scans yet
          </p>
        )}

        {scans.map((scan) => {
          const isActive = scan.id === activeScanId;

          return (
            <div
              key={scan.id}
              onClick={() => onSelectScan(scan.id)}
              className={`group relative flex items-center justify-center px-3 py-2 rounded-lg cursor-pointer text-sm transition ${
                isActive
                  ? "bg-neutral-800 text-white"
                  : "text-neutral-300 hover:bg-neutral-900"
              }`}
            >
              <div className="flex items-center gap-2 overflow-hidden">
                <span
                  className={`w-1.5 h-1.5 rounded-full shrink-0 ${severityDot(
                    scan.risk_level
                  )}`}
                />
                <div className="flex flex-col overflow-hidden items-center text-center">
                  <span className="truncate">
                    {scan.contract_name || `Scan #${scan.id}`}
                  </span>
                  <span className="text-[11px] text-neutral-600">
                    {timeAgo(scan.created_at)}
                  </span>
                </div>
              </div>

              <button
                onClick={(e) =>
                  handleDelete(
                    scan.id,
                    scan.contract_name || `Scan #${scan.id}`,
                    e
                  )
                }
                className="opacity-0 group-hover:opacity-100 text-neutral-500 hover:text-red-400 text-xs absolute right-2"
                aria-label="Delete scan"
              >
                ✕
              </button>
            </div>
          );
        })}
      </div>

      {/* Footer */}
      <div className="border-t border-neutral-800 p-3 flex justify-center">
        <span className="text-xs text-neutral-400">ContractShield</span>
      </div>
    </aside>
  );
}