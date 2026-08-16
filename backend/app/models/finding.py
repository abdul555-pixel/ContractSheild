from pydantic import BaseModel, field_validator 

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


class AuditRequest(BaseModel):
    contract: str

    @field_validator("contract")
    @classmethod
    def validate_contract(cls, value: str) -> str:

        # Reject empty contracts
        if not value.strip():
            raise ValueError(
                "Contract code cannot be empty."
            )

        # Maximum 1 MB
        max_size = 1 * 1024 * 1024

        if len(value.encode("utf-8")) > max_size:
            raise ValueError(
                "Contract must be smaller than 1 MB."
            )

        return value