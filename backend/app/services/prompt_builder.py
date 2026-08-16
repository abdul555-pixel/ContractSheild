from app.models.finding import Finding


def build_audit_prompt(
    finding: Finding,
    source_code: str
) -> str:

    return f"""
You are an expert Solidity smart contract security auditor.

Analyze ONE Slither finding.

==================================================
SLITHER FINDING
==================================================

Detector:
{finding.title}

Description:
{finding.description}

Severity:
{finding.severity}

Function:
{finding.function_name}

Affected lines:
{finding.line_numbers}

==================================================
SOURCE CODE
==================================================

{source_code}

==================================================
IMPORTANT ANALYSIS RULE
==================================================

You MUST analyze ONLY this Slither detector:

{finding.title}

Do not replace it with another vulnerability that happens
to exist in the source code.

Special rules:

1. If the detector is "reentrancy-eth":
   Analyze the reentrancy vulnerability.

2. If the detector is "solc-version":
   Analyze ONLY the Solidity compiler version.
   Do NOT discuss reentrancy.
   Do NOT discuss msg.sender.call.
   Do NOT discuss balances.

3. If the detector is "low-level-calls":
   Analyze the use of the low-level call.
   You may mention reentrancy as a related risk ONLY if
   the Slither description supports it.

==================================================
CODE EXTRACTION RULE
==================================================

The "original_code" field MUST contain the EXACT Solidity
source code from the supplied source code.

Do NOT invent comments.

Do NOT add comments such as:
"// VULNERABILITY"

Do NOT rewrite the source code.

The "patched_code" field should contain only the corrected
version of the relevant code.

==================================================
JSON RULES
==================================================

Return ONLY valid JSON.

Do NOT use Markdown.

Do NOT use ```json.

The response MUST contain exactly these fields:

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

IMPORTANT:

Because this is JSON, ALL newlines inside original_code
and patched_code MUST be escaped as \\n.

ALL double quotes inside Solidity strings MUST be escaped
as \\\".

Example:

"original_code": "require(success, \\\"Transfer failed\\\");\\n"

Never place a literal newline inside a JSON string.

exploitability MUST be exactly:

"High"

"Medium"

or

"Low"

Do not return an array.

Do not include any text outside the JSON object.
"""