import json
import os
import re
import tempfile
import time

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.finding import LLMAssessment
from app.services.llm_service import ask_llm
from app.services.patch_generator import generate_patch
from app.services.prompt_builder import build_audit_prompt
from app.services.scan_repository import save_scan
from app.services.severity_scorer import compute_risk_score
from app.services.slither_parser import parse_slither_output
from app.services.slither_service import run_slither_scan 

router = APIRouter(
    prefix="/audit",
    tags=["Audit"],
)


# ============================================================
# SECURITY SETTINGS
# ============================================================

# Maximum Solidity source-code size: 1 MB
MAX_CONTRACT_SIZE = 1 * 1024 * 1024

# Basic demo rate limiting
RATE_LIMIT_REQUESTS = 5
RATE_LIMIT_WINDOW = 60  # seconds

scan_requests = {}


# ============================================================
# REQUEST MODEL
# ============================================================

class AuditRequest(BaseModel):
    contract: str
    contract_name: str | None = None


# ============================================================
# RATE LIMITING
# ============================================================

def check_rate_limit(client_id: str):
    """
    Basic in-memory rate limiter.

    Allows at most 5 scans per IP address
    within a 60-second window.
    """
    now = time.time()
    requests = scan_requests.get(client_id, [])

    # Remove requests outside the current window
    requests = [
        timestamp for timestamp in requests if now - timestamp < RATE_LIMIT_WINDOW
    ]

    if len(requests) >= RATE_LIMIT_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail="Too many scan requests. Please wait before trying again.",
        )

    requests.append(now)
    scan_requests[client_id] = requests


# ============================================================
# JSON FIELD REPAIR HELPER
# ============================================================

def repair_code_field(text: str, field_name: str) -> str:
    marker = f'"{field_name}"'
    start_pos = text.find(marker)

    if start_pos == -1:
        return text

    colon_pos = text.find(":", start_pos + len(marker))
    if colon_pos == -1:
        return text

    quote_pos = text.find('"', colon_pos + 1)
    if quote_pos == -1:
        return text

    content_start = quote_pos + 1
    repaired = []
    escaped = False
    i = content_start

    while i < len(text):
        char = text[i]

        # Possible closing quote of the JSON field
        if char == '"' and not escaped:
            remainder = text[i + 1 :].lstrip()
            if remainder.startswith(",") or remainder.startswith("}"):
                return text[:content_start] + "".join(repaired) + text[i:]
            else:
                repaired.append('\\"')
                i += 1
                continue

        # Preserve existing escape sequences
        if char == "\\" and not escaped:
            repaired.append(char)
            escaped = True
            i += 1
            continue

        # Escape raw control characters
        if char == "\n":
            repaired.append("\\n")
        elif char == "\r":
            repaired.append("\\r")
        elif char == "\t":
            repaired.append("\\t")
        else:
            repaired.append(char)

        escaped = False
        i += 1

    return text


# ============================================================
# LLM RESPONSE PARSER
# ============================================================

def parse_llm_response(response: str) -> LLMAssessment:
    response = response.strip()

    # Remove accidental markdown code fences
    response = re.sub(r"^```json\s*", "", response, flags=re.IGNORECASE)
    response = re.sub(r"^```\s*", "", response)
    response = re.sub(r"\s*```$", "", response)

    repaired_response = repair_code_field(response, "original_code")
    repaired_response = repair_code_field(repaired_response, "patched_code")

    try:

        decoder = json.JSONDecoder()
        data, _ = decoder.raw_decode(repaired_response)

    except json.JSONDecodeError as e:

        raise ValueError(
            f"LLM returned invalid JSON: {e}"
        )

    if not isinstance(data, dict):
        raise ValueError("LLM response must be a JSON object")

    return LLMAssessment(**data)


# ============================================================
# AUDIT ENDPOINT
# ============================================================

@router.post("/")
async def audit_contract(
    request: Request,
    audit_request: AuditRequest,
    db: Session = Depends(get_db),
):
    # 1. RATE LIMIT
    client_id = request.client.host if request.client else "unknown"
    check_rate_limit(client_id)

    # 2. VALIDATE CONTRACT INPUT
    contract = audit_request.contract

    if not contract.strip():
        raise HTTPException(
            status_code=400,
            detail="Contract cannot be empty."
        )

    contract_size = len(contract.encode("utf-8"))
    if contract_size > MAX_CONTRACT_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Contract is too large. Maximum size is 1 MB."
        )

    if "pragma solidity" not in contract.lower():
        raise HTTPException(
            status_code=400,
            detail="The submitted file does not appear to be a Solidity contract."
        )

    temp_contract_path = None

    try:
        # 3. SAVE CONTRACT TEMPORARILY
        with tempfile.NamedTemporaryFile(
            suffix=".sol", mode="w", encoding="utf-8", delete=False
        ) as temp_file:
            temp_file.write(contract)
            temp_contract_path = temp_file.name

        # 4. RUN SLITHER
        slither_output = run_slither_scan(temp_contract_path)

        if not slither_output.get("success", False):
            raise HTTPException(
                status_code=400,
                detail=slither_output.get("error", "Slither analysis failed")
            )

        # 5. PARSE SLITHER FINDINGS
        findings = parse_slither_output(slither_output["data"])

        # 6. NO VULNERABILITIES
        if not findings:
            saved_scan = save_scan(
                db,
                contract_name=audit_request.contract_name or "Untitled Contract",
                contract_code=contract,
                risk_score=1,
                risk_level="Low",
                findings_json=[],
            )
            return {
                "scan_id": saved_scan.id,
                "risk_score": 1,
                "risk_level": "Low",
                "findings": [],
                "llm_assessments": []
            }

        # 7. ANALYZE EACH FINDING WITH THE LLM
        assessments = []
        for index, finding in enumerate(findings):
            try:
                prompt = build_audit_prompt(finding, contract)
                llm_response = ask_llm(prompt)

                print(f"\n--- FINDING {index + 1} ---")
                print(f"Title: {finding.title}")
                print("\n--- LLM RESPONSE ---")
                print(llm_response)
                print("--------------------\n")

                assessment = parse_llm_response(llm_response)
                assessments.append(assessment)

            except Exception as e:
                print("\n========== LLM ERROR ==========")
                print(finding.title)
                print(repr(e))
                print("================================\n")

                fallback_assessment = LLMAssessment(
                    title=finding.title,
                    plain_explanation=finding.description,
                    impact="This issue should be reviewed before deploying the contract.",
                    exploitability="Medium",
                    exploitability_reason=(
                        "The AI assessment could not be generated, "
                        "so a conservative default rating was applied."
                    ),
                    suggested_fix=(
                        "Review the Slither finding and apply the recommended "
                        "Solidity security pattern."
                    ),
                    original_code="",
                    patched_code=""
                )
                assessments.append(fallback_assessment)

        # 8. CALCULATE SCORE FOR EACH FINDING
        scored_findings = []
        for finding, assessment in zip(findings, assessments):
            score = compute_risk_score(finding, assessment)
            scored_findings.append(
                {
                    "finding": finding.model_dump(),
                    "assessment": assessment.model_dump(),
                    "risk_score": score
                }
            )

        # 9. OVERALL RISK SCORE
        overall_score = max(item["risk_score"] for item in scored_findings)

        if overall_score >= 8:
            risk_level = "Critical"
        elif overall_score >= 6:
            risk_level = "High"
        elif overall_score >= 4:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        # 10. SAVE SCAN TO DATABASE
        saved_scan = save_scan(
            db,
            contract_name=getattr(audit_request, "contract_name", "Untitled Contract"),
            contract_code=contract,
            risk_score=overall_score,
            risk_level=risk_level,
            findings_json=scored_findings,
        )

        # 11. RETURN RESULT
        return {
            "scan_id": saved_scan.id,
            "risk_score": overall_score,
            "risk_level": risk_level,
            "findings": scored_findings
        }

    except HTTPException:
        raise

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Audit failed: {str(e)}"
        )

    finally:
        # 12. CLEANUP TEMPORARY FILE
        if temp_contract_path and os.path.exists(temp_contract_path):
            try:
                os.remove(temp_contract_path)
            except OSError:
                pass