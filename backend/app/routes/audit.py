import json
import os
import re
import tempfile
import time

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.models.finding import LLMAssessment
from app.services.slither_service import run_slither_scan
from app.services.slither_parser import parse_slither_output
from app.services.prompt_builder import build_audit_prompt
from app.services.llm_service import ask_llm
from app.services.severity_scorer import compute_risk_score
from app.services.patch_generator import generate_patch


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

    requests = scan_requests.get(
        client_id,
        []
    )

    # Remove requests outside the current window
    requests = [
        timestamp
        for timestamp in requests
        if now - timestamp < RATE_LIMIT_WINDOW
    ]

    if len(requests) >= RATE_LIMIT_REQUESTS:

        raise HTTPException(
            status_code=429,
            detail=(
                "Too many scan requests. "
                "Please wait before trying again."
            )
        )

    requests.append(now)

    scan_requests[client_id] = requests


# ============================================================
# LLM RESPONSE PARSER
# ============================================================

def parse_llm_response(
    response: str
) -> list[LLMAssessment]:
    """
    Convert the LLM's JSON response into
    LLMAssessment objects.
    """

    response = response.strip()

    # Remove accidental markdown code fences
    response = re.sub(
        r"^```json\s*",
        "",
        response,
        flags=re.IGNORECASE
    )

    response = re.sub(
        r"\s*```$",
        "",
        response
    )

    try:

        data = json.loads(response)

    except json.JSONDecodeError as e:

        raise ValueError(
            f"LLM returned invalid JSON: {e}"
        )

    if not isinstance(data, list):

        raise ValueError(
            "LLM response must be a JSON list"
        )

    return [
        LLMAssessment(**item)
        for item in data
    ]


# ============================================================
# AUDIT ENDPOINT
# ============================================================

@router.post("/")
async def audit_contract(
    request: Request,
    audit_request: AuditRequest,
):

    # ========================================================
    # 1. RATE LIMIT
    # ========================================================

    client_id = (
        request.client.host
        if request.client
        else "unknown"
    )

    check_rate_limit(client_id)

    # ========================================================
    # 2. VALIDATE CONTRACT INPUT
    # ========================================================

    contract = audit_request.contract

    # Reject empty contracts
    if not contract.strip():

        raise HTTPException(
            status_code=400,
            detail="Contract cannot be empty."
        )

    # ========================================================
    # Maximum size: 1 MB
    # ========================================================

    contract_size = len(
        contract.encode("utf-8")
    )

    if contract_size > MAX_CONTRACT_SIZE:

        raise HTTPException(
            status_code=413,
            detail=(
                "Contract is too large. "
                "Maximum size is 1 MB."
            )
        )

    # ========================================================
    # Basic Solidity validation
    # ========================================================

    if "pragma solidity" not in contract.lower():

        raise HTTPException(
            status_code=400,
            detail=(
                "The submitted file does not appear "
                "to be a Solidity contract."
            )
        )

    temp_contract_path = None

    try:

        # ====================================================
        # 3. SAVE CONTRACT TEMPORARILY
        # ====================================================

        with tempfile.NamedTemporaryFile(
            suffix=".sol",
            mode="w",
            encoding="utf-8",
            delete=False
        ) as temp_file:

            temp_file.write(contract)

            temp_contract_path = temp_file.name

        # ====================================================
        # SECURITY
        #
        # The uploaded Solidity contract is NEVER executed.
        #
        # It is only passed to Slither for STATIC ANALYSIS.
        # ====================================================

        # ====================================================
        # 4. RUN SLITHER
        # ====================================================

        slither_output = run_slither_scan(
            temp_contract_path
        )

        if not slither_output.get(
            "success",
            False
        ):

            raise HTTPException(
                status_code=400,
                detail=slither_output.get(
                    "error",
                    "Slither analysis failed"
                )
            )

        # ====================================================
        # 5. PARSE SLITHER FINDINGS
        # ====================================================

        findings = parse_slither_output(
            slither_output["data"]
        )

        # ====================================================
        # 6. NO VULNERABILITIES
        # ====================================================

        if not findings:

            return {
                "risk_score": 1,
                "risk_level": "Low",
                "findings": [],
                "llm_assessments": []
            }

        # ====================================================
        # 7. BUILD LLM PROMPT
        # ====================================================

        prompt = build_audit_prompt(
            findings
        )

        # ====================================================
        # 8. ASK LLM
        # ====================================================

        llm_response = ask_llm(
            prompt
        )

        # ====================================================
        # 9. PARSE LLM JSON
        # ====================================================

        assessments = parse_llm_response(
            llm_response
        )

        # ====================================================
        # 10. MAKE SURE COUNTS MATCH
        # ====================================================

        if len(assessments) != len(findings):

            raise ValueError(
                f"LLM returned "
                f"{len(assessments)} assessments "
                f"for "
                f"{len(findings)} findings"
            )

        # ====================================================
        # 11. GENERATE PATCHES
        # ====================================================

        patched_assessments = []

        for finding, assessment in zip(
            findings,
            assessments
        ):

            patch = generate_patch(
                contract=contract,
                finding=finding
            )

            assessment = assessment.model_copy(
                update={
                    "original_code": patch[
                        "original_code"
                    ],
                    "patched_code": patch[
                        "patched_code"
                    ]
                }
            )

            patched_assessments.append(
                assessment
            )

        assessments = patched_assessments

        # ====================================================
        # 12. CALCULATE SCORE FOR EACH FINDING
        # ====================================================

        scored_findings = []

        for finding, assessment in zip(
            findings,
            assessments
        ):

            score = compute_risk_score(
                finding,
                assessment
            )

            scored_findings.append(
                {
                    "finding": finding.model_dump(),
                    "assessment": assessment.model_dump(),
                    "risk_score": score
                }
            )

        # ====================================================
        # 13. OVERALL RISK SCORE
        # ====================================================

        overall_score = max(
            item["risk_score"]
            for item in scored_findings
        )

        if overall_score >= 8:

            risk_level = "Critical"

        elif overall_score >= 6:

            risk_level = "High"

        elif overall_score >= 4:

            risk_level = "Medium"

        else:

            risk_level = "Low"

        # ====================================================
        # 14. RETURN FINAL RESULT
        # ====================================================

        return {
            "risk_score": overall_score,
            "risk_level": risk_level,
            "findings": scored_findings
        }

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Audit failed: {str(e)}"
        )

    finally:

        # ====================================================
        # 15. DELETE TEMPORARY SOLIDITY FILE
        # ====================================================

        if (
            temp_contract_path
            and os.path.exists(temp_contract_path)
        ):

            try:

                os.remove(
                    temp_contract_path
                )

            except OSError:

                pass