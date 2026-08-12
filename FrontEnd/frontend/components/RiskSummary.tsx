interface RiskSummaryProps {
  totalFindings: number;
  high: number;
  medium: number;
  low: number;
  riskScore: number;
}

export default function RiskSummary({
  totalFindings,
  high,
  medium,
  low,
  riskScore,
}: RiskSummaryProps) {
  const getRiskLabel = () => {
    if (riskScore >= 80) return "Critical Risk";
    if (riskScore >= 60) return "High Risk";
    if (riskScore >= 40) return "Medium Risk";
    if (riskScore >= 20) return "Low Risk";

    return "Minimal Risk";
  };

  return (
    <div className="rounded-2xl border border-neutral-800 bg-neutral-900 p-6">
      <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">

        {/* Overall Risk */}
        <div>
          <p className="text-sm text-neutral-500">
            Overall Risk Score
          </p>

          <div className="mt-2 flex items-baseline gap-3">
            <span className="text-4xl font-bold text-white">
              {riskScore}
            </span>

            <span className="text-sm text-red-400">
              {getRiskLabel()}
            </span>
          </div>
        </div>

        {/* Total Findings */}
        <div>
          <p className="text-sm text-neutral-500">
            Total Findings
          </p>

          <p className="mt-2 text-3xl font-semibold text-white">
            {totalFindings}
          </p>
        </div>

        {/* Severity Breakdown */}
        <div>
          <p className="text-sm text-neutral-500 mb-3">
            Severity Breakdown
          </p>

          <div className="flex gap-5">

            <div>
              <p className="text-xl font-semibold text-red-400">
                {high}
              </p>

              <p className="text-xs text-neutral-500">
                High
              </p>
            </div>

            <div>
              <p className="text-xl font-semibold text-yellow-400">
                {medium}
              </p>

              <p className="text-xs text-neutral-500">
                Medium
              </p>
            </div>

            <div>
              <p className="text-xl font-semibold text-blue-400">
                {low}
              </p>

              <p className="text-xs text-neutral-500">
                Low
              </p>
            </div>

          </div>
        </div>

      </div>
    </div>
  );
}