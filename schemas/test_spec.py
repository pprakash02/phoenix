from pydantic import BaseModel
from typing import Dict, List, Any


class TestSpec(BaseModel):
    input: Any
    expected_behavior: str
    expected_result: Any

class AnalystOutput(BaseModel):
    function_name: str
    business_logic_summary: str
    successful_mappings: List[Dict[str, Any]]
    crashes: List[Dict[str, Any]]
    edge_cases: List[Dict[str, Any]]