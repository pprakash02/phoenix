from pydantic import BaseModel
from typing import List, Any


class TestSpec(BaseModel):
    input: Any
    expected_behavior: str
    expected_result: Any

class AnalystOutput(BaseModel):
    function_under_test: str
    business_logic_summary: str
    test_specs: List[TestSpec]