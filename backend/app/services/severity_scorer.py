from app.models.finding import Finding, LLMAssessment


SLITHER_WEIGHTS = {
    "High": 4,
    "Medium": 2,
    "Low": 1,
}

EXPLOITABILITY_WEIGHTS = {
    "High": 4,
    "Medium": 2,
    "Low": 1,
}


def compute_risk_score(
    finding: Finding,
    llm_assessment: LLMAssessment
) -> int:

    slither_weight = SLITHER_WEIGHTS.get(
        finding.severity,
        1
    )

    exploitability_weight = EXPLOITABILITY_WEIGHTS.get(
        llm_assessment.exploitability,
        1
    )

    raw_score = slither_weight + exploitability_weight

    normalized_score = 1 + ((raw_score - 2) / 6) * 9

    return round(normalized_score)