from pydantic import BaseModel, Field
from typing import List, Optional


class Finding(BaseModel):
    rule_id: str = Field(description="Identifier like SEC001 or LLM001")
    file_path: str = Field(description="Relative path of the file scanned")
    line_number: int = Field(description="Line number where the issue occurs")
    severity: str = Field(description="CRITICAL, HIGH, MEDIUM, or LOW")
    title: str = Field(description="Short description of the issue")
    explanation: str = Field(description="Detailed risk explanation")
    suggested_fix: str = Field(description="Refactored code snippet or remediation advice")


class ReviewResponse(BaseModel):
    verdict: str = Field(description="APPROVE, REQUEST_CHANGES, or COMMENT")
    summary: str = Field(description="High-level summary of the security review")
    findings: List[Finding] = Field(default_factory=list)