from pydantic import BaseModel, Field
from typing import List, Optional

class ValidationIssue(BaseModel):
    test_name: str = Field(description="The name of the test function with the issue.")
    issue_type: str = Field(description="Category: 'Hallucination', 'Syntax Error', or 'Missing Coverage'.")
    description: str = Field(description="Detailed explanation of what needs to be fixed.")

class CriticReport(BaseModel):
    is_approved: bool = Field(description="True if the test suite is ready for production, False otherwise.")
    score: int = Field(ge=0, le=100, description="Confidence score of the test suite quality.")
    issues: List[ValidationIssue] = Field(default=[], description="List of specific problems found.")
    recommendation: Optional[str] = Field(description="Overall advice for the QA Engineer to improve the code.")