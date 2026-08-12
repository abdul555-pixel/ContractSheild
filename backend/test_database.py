from app.db.session import save_scan, get_scan_by_id


contract_code = """
pragma solidity ^0.8.0;

contract TestContract {
    uint256 public value;

    function setValue(uint256 _value) public {
        value = _value;
    }
}
"""

findings = [
    {
        "title": "Example Finding",
        "description": "Test security finding",
        "severity": "Low",
        "function_name": "setValue",
        "line_numbers": [8],
    }
]

risk_score = 2


print("Saving scan...")

scan_id = save_scan(
    contract_code=contract_code,
    findings=findings,
    risk_score=risk_score,
)

print(f"Scan saved with ID: {scan_id}")


print("Retrieving scan...")

scan = get_scan_by_id(scan_id)

if scan:
    print("Scan found!")
    print("ID:", scan.id)
    print("Contract:", scan.contract_code)
    print("Total findings:", scan.total_findings)
    print("Risk:", scan.overall_risk)
    print("Findings:", scan.findings_json)
    print("Created:", scan.created_at)
else:
    print("Scan not found.")
