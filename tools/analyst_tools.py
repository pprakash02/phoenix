import json
from typing import Annotated, List, Dict, Any
from pydantic import Field
from agent_framework import tool
import re


@tool(approval_mode="never_require")
def parse_runtime_logs(raw_output: str) -> List[Dict[str, Any]]:
    logs = []
    for line in raw_output.splitlines():
        line = line.strip()
        # Look for JSON objects on individual lines
        if line.startswith("{") and line.endswith("}"):
            try:
                logs.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return logs


@tool(approval_mode="never_require")
def detect_function(logs: List[Dict[str, Any]]) -> str:
    """
    Detect the function name from runtime logs.
    """

    if not logs:
        return "unknown"

    return logs[0].get("function", "unknown")


@tool(approval_mode="never_require")
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