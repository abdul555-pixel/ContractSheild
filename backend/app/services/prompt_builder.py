from app.models.finding import Finding


def build_audit_prompt(findings: list[Finding]) -> str:
    return f"""
You are a smart contract security auditor.

Analyze the following Slither findings.

For EACH finding, provide exactly these fields:

1. title
2. plain_explanation
   - Explain the vulnerability in simple, developer-friendly language.
3. impact
   - Explain what could happen if the vulnerability is exploited.
4. exploitability
   - Classify as exactly one of: "High", "Medium", or "Low".
5. exploitability_reason
   - Explain why you gave that exploitability rating.
6. suggested_fix
   - Explain how the developer should fix the vulnerability.
7. original_code
   - Include the exact vulnerable Solidity code snippet from the provided
     contract.
   - Do not invent, rewrite, or modify the original code.
8. patched_code
   - Provide a corrected version of ONLY the vulnerable snippet.
   - Do not rewrite the entire contract.
   - The patch is a SUGGESTION for the developer to review.
   - Never claim that the patch is guaranteed safe.

When generating a patch:

- Preserve the original functionality as much as possible.
- Follow established Solidity security patterns.
- For reentrancy vulnerabilities, prefer the Checks-Effects-Interactions
  pattern where appropriate.
- Do not introduce unrelated changes.
- If the exact vulnerable code cannot be identified from the provided
  information, use an empty string for original_code and patched_code rather
  than inventing code.

Return ONLY a valid JSON array.

Each array item MUST contain exactly these fields:

[
  {{
    "title": "...",
    "plain_explanation": "...",
    "impact": "...",
    "exploitability": "High",
    "exploitability_reason": "...",
    "suggested_fix": "...",
    "original_code": "...",
    "patched_code": "..."
  }}
]

Do not wrap the JSON in markdown code fences.
Do not include any additional text before or after the JSON.

Slither findings:

{findings}
"""