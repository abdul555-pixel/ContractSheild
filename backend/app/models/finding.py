from pydantic import BaseModel


class Finding(BaseModel):
    title: str
    description: str
    severity: str
    function_name: str
    line_numbers: list[int]


class LLMAssessment(BaseModel):
    title: str
    plain_explanation: str
    impact: str
    exploitability: str
    exploitability_reason: str
    suggested_fix: str
    original_code: str
    patched_code: str