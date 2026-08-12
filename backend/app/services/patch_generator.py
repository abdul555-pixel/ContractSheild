import json
import os

from openai import OpenAI

from app.models.finding import Finding


def build_patch_prompt(
    contract: str,
    finding: Finding
) -> str:

    return f"""
You are an expert Solidity security auditor.

You are given:

1. The complete Solidity smart contract.
2. One security finding detected by static analysis.

Your task is to generate a minimal patch for ONLY this finding.

SECURITY FINDING
----------------
Title:
{finding.title}

Description:
{finding.description}

Severity:
{finding.severity}

Function:
{finding.function_name}

Line numbers:
{finding.line_numbers}

SOLIDITY CONTRACT
-----------------
```solidity
{contract}

STRICT RULES

Find the vulnerable code responsible for this finding.
Return the EXACT original Solidity code from the contract.
Do NOT invent or rewrite the original code.
Create a corrected version of ONLY the vulnerable section.
Keep the patch as small as possible.
Do not modify unrelated functions.
Preserve the existing contract logic wherever possible.
The patched code must be valid Solidity.
Do not include markdown code fences inside the JSON values.
Return ONLY valid JSON.

Return exactly this structure:

{{
"original_code": "exact vulnerable code from the contract",
"patched_code": "corrected version of the vulnerable code",
"explanation": "short explanation of what was changed"
}}
"""

def generate_patch(
        contract: str,
        finding: Finding
        ) -> dict:

        api_key = os.getenv("OPENROUTER_API_KEY")

        model = os.getenv(
            "OPENROUTER_MODEL",
            "meta-llama/llama-3.1-8b-instruct:free"
        )

        if not api_key:
            raise ValueError(
                "OPENROUTER_API_KEY is not configured."
            )

        client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )

        prompt = build_patch_prompt(
            contract,
            finding
        )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert Solidity security "
                        "auditor and patch generator. "
                        "Return only valid JSON."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError(
                "Patch generator returned an empty response."
            )

        content = content.strip()

        # Remove accidental markdown code fences
        if content.startswith("```json"):
            content = content[len("```json"):].strip()

        elif content.startswith("```"):
            content = content[len("```"):].strip()

        if content.endswith("```"):
            content = content[:-3].strip()

        try:
            patch = json.loads(content)

        except json.JSONDecodeError as e:
            raise ValueError(
                f"Patch generator returned invalid JSON: {e}"
            )

        required_fields = [
            "original_code",
            "patched_code",
            "explanation"
        ]

        for field in required_fields:
            if field not in patch:
                raise ValueError(
                    f"Patch generator response is missing "
                    f"'{field}'."
                )

        return patch