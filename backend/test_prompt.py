import json
from app.models.finding import Finding


def build_audit_prompt(findings: list[Finding]) -> str:
    findings_data = [
        {
            "title": finding.title,
            "description": finding.description,
            "severity": finding.severity,
            "function_name": finding.function_name,
            "line_numbers": finding.line_numbers,
        }
        for finding in findings
    ]

    findings_json = json.dumps(findings_data, indent=2)

    prompt = f"""
You are a smart contract security auditor.

Given the following static analysis findings from Slither, analyze each
finding independently.

For each finding:

1. Explain the vulnerability in plain English in 2-3 sentences.
2. Explain the real-world impact if it is exploited.
3. Rate exploitability as exactly one of: High, Medium, Low.
4. Give a one-sentence reason for the exploitability rating.
5. Suggest a concrete code fix.

Important rules:
- Base your analysis only on the provided Slither findings.
- Do not invent vulnerabilities that Slither did not report.
- Do not exaggerate the severity.
- Keep explanations understandable to a Solidity developer.
- The suggested fix should be practical and specific.

Respond ONLY with valid JSON.

The JSON must match this structure exactly:

[
  {{
    "title": "...",
    "plain_explanation": "...",
    "impact": "...",
    "exploitability": "High/Medium/Low",
    "exploitability_reason": "...",
    "suggested_fix": "..."
  }}
]

Slither findings:

{findings_json}
"""

    return prompt