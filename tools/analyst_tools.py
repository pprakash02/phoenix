import re
from typing import List
from pydantic import Field
from agent_framework import tool

@tool
def search_logs(
    log_text: str = Field(description="The log text to search within."),
    pattern: str = Field(description="The regex pattern to search for.")
) -> List[str]:
    """Search the log text for lines that match a given regex pattern."""
    lines = log_text.splitlines()
    matches = [line for line in lines if re.search(pattern, line)]
    return matches

@tool
def extract_numbers(
    log_text: str = Field(description="The log text to extract numbers from.")
) -> List[float]:
    """Extract all floating-point numbers from the log text."""
    # Find all numbers (including decimals, optional sign)
    numbers = re.findall(r"-?\d+\.?\d*", log_text)
    return [float(num) for num in numbers]

@tool
def count_occurrences(
    log_text: str = Field(description="The log text."),
    substring: str = Field(description="The substring to count.")
) -> int:
    """Count the number of occurrences of a substring in the log text."""
    return log_text.count(substring)