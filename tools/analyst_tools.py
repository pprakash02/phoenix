import json
from typing import Annotated, List, Dict, Any
from pydantic import Field
from agent_framework import tool
import re


@tool(approval_mode="never_require")
def parse_runtime_logs(raw_output: str) -> List[Dict[str, Any]]:
    """
    Parse runtime logs from Observer output.
    Handles JSON objects per-line, JSON arrays, and JSON embedded in markdown code blocks.
    """
    logs: List[Dict[str, Any]] = []

    # Strategy 1: Try to parse the entire input as a JSON array
    try:
        parsed = json.loads(raw_output.strip())
        if isinstance(parsed, list):
            return [item for item in parsed if isinstance(item, dict)]
    except (json.JSONDecodeError, ValueError):
        pass

    # Strategy 2: Extract JSON from markdown code fences (```json ... ```)
    code_block_pattern = re.compile(r'```(?:json)?\s*\n(.*?)```', re.DOTALL)
    for match in code_block_pattern.finditer(raw_output):
        block = match.group(1).strip()
        try:
            parsed = json.loads(block)
            if isinstance(parsed, list):
                logs.extend(item for item in parsed if isinstance(item, dict))
                continue
            elif isinstance(parsed, dict):
                logs.append(parsed)
                continue
        except (json.JSONDecodeError, ValueError):
            pass
        # If the block isn't valid JSON as a whole, try line-by-line
        for line in block.splitlines():
            line = line.strip().rstrip(',')
            if line.startswith("{") and line.endswith("}"):
                try:
                    logs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    if logs:
        return logs

    # Strategy 3: Fallback — scan every line for individual JSON objects
    for line in raw_output.splitlines():
        line = line.strip()
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

    def _safe_value(val):
        """Convert non-standard floats to strings for safe JSON serialization."""
        if isinstance(val, float):
            if val == float('inf'):
                return "Infinity"
            if val == float('-inf'):
                return "-Infinity"
            if val != val:  # NaN check
                return "NaN"
        return val

    successes = []
    crashes = []
    edges = []

    for log in logs:
        inp = log["inputs"]["args"][0]

        if log["status"] == "success":
            successes.append({
                "input": inp,
                "output": _safe_value(log["output"])
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