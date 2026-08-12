import RiskSummary from "@/components/RiskSummary";
import FindingCard from "@/components/FindingCard";

const mockAudit = {
  riskScore: 78,

  findings: [
    {
      title: "Reentrancy Vulnerability",
      severity: "High" as const,
      functionName: "withdraw",

      description:
        "The contract sends Ether before updating the user's balance. A malicious contract could potentially call the withdrawal function again before the balance is updated. Updating the balance before making the external call helps prevent this risk.",

      originalCode: `function withdraw(uint256 amount) public {
    require(balances[msg.sender] >= amount);

    (bool success, ) = msg.sender.call{value: amount}("");
    require(success);

    balances[msg.sender] -= amount;
}`,

      patchedCode: `function withdraw(uint256 amount) public {
    require(balances[msg.sender] >= amount);

    balances[msg.sender] -= amount;

    (bool success, ) = msg.sender.call{value: amount}("");
    require(success);
}`,
    },

    {
      title: "Missing Access Control",
      severity: "Medium" as const,
      functionName: "setFee",

      description:
        "This function can be called without checking whether the caller has permission to change the contract fee. An unauthorized account could potentially modify this value.",

      originalCode: `function setFee(uint256 newFee) public {
    fee = newFee;
}`,

      patchedCode: `function setFee(uint256 newFee) public onlyOwner {
    fee = newFee;
}`,
    },

    {
      title: "Unchecked Return Value",
      severity: "Low" as const,
      functionName: "sendToken",

      description:
        "The return value from the token transfer operation is not checked. Checking the result helps ensure that a failed operation does not go unnoticed.",

      originalCode: `function sendToken(
    address token,
    address recipient,
    uint256 amount
) public {
    IERC20(token).transfer(recipient, amount);
}`,

      patchedCode: `function sendToken(
    address token,
    address recipient,
    uint256 amount
) public {
    bool success = IERC20(token).transfer(
        recipient,
        amount
    );

    require(success, "Transfer failed");
}`,
    },
  ],
};

export default function ScanPage() {
  const findings = mockAudit.findings;

  const highCount = findings.filter(
    (finding) => finding.severity === "High"
  ).length;

  const mediumCount = findings.filter(
    (finding) => finding.severity === "Medium"
  ).length;

  const lowCount = findings.filter(
    (finding) => finding.severity === "Low"
  ).length;

  return (
    <main className="min-h-screen bg-[#0A0A0A] text-white">

      {/* Navbar */}
      <header className="w-full border-b border-neutral-800 px-8 py-5">
        <div className="max-w-6xl mx-auto">
          <h1 className="font-semibold text-lg">
            ContractShield
          </h1>
        </div>
      </header>

      {/* Main Content */}
      <section className="max-w-6xl mx-auto px-6 py-12">

        {/* Page Header */}
        <div className="mb-8">
          <p className="text-sm text-neutral-500 mb-2">
            Security Audit
          </p>

          <h1 className="text-3xl font-bold tracking-tight">
            Smart Contract Analysis
          </h1>

          <p className="mt-2 text-neutral-400">
            Review the vulnerabilities detected in your smart contract.
          </p>
        </div>

        {/* Risk Summary */}
        <RiskSummary
          totalFindings={findings.length}
          high={highCount}
          medium={mediumCount}
          low={lowCount}
          riskScore={mockAudit.riskScore}
        />

        {/* Findings */}
        <div className="mt-10">

          <div className="flex items-center justify-between mb-5">
            <h2 className="text-xl font-semibold">
              Findings
            </h2>

            <span className="text-sm text-neutral-500">
              {findings.length} issues detected
            </span>
          </div>

          {/* Finding Cards */}
          <div className="space-y-4">
            {findings.map((finding, index) => (
              <FindingCard
                key={index}
                title={finding.title}
                severity={finding.severity}
                functionName={finding.functionName}
                description={finding.description}
                originalCode={finding.originalCode}
                patchedCode={finding.patchedCode}
              />
            ))}
          </div>

        </div>
      </section>
    </main>
  );
}