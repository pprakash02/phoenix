import json
from typing import Annotated, List, Dict, Any
from pydantic import Field
from agent_framework import tool
import re


@tool
def parse_runtime_logs(
    raw_output: str = Field(description="Raw observer output containing JSON logs")
) -> List[Dict[str, Any]]:
    """
    Extract JSON runtime logs embedded in observer output.
    """

    # find JSON array in the text
    match = re.search(r"\[\s*{.*}\s*\]", raw_output, re.DOTALL)

    if not match:
        return []

    json_block = match.group(0)

    try:
        logs = json.loads(json_block)
        return logs
    except Exception:
        return []

@tool
def detect_function(logs: List[Dict[str, Any]]) -> str:
    """
    Detect the function name from runtime logs.
    """

    if not logs:
        return "unknown"

    return logs[0].get("function", "unknown")


@tool
def summarize_execution_results(logs: List[Dict[str, Any]]) -> Dict:
    """
    Convert runtime logs into behavioral specification.
    """

    successes = []
    crashes = []
    edges = []

    for log in logs:
        inp = log["inputs"]["args"][0]

        if log["status"] == "success":
            successes.append({
                "input": inp,
                "output": log["output"]
            })
        else:
            crashes.append({
                "input": inp,
                "error": log["error"]
            })

    return {
        "successful_mappings": successes,
        "crashes": crashes,
        "edge_cases": edges
    }