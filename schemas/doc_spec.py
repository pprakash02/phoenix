# schemas/doc_spec.py
from pydantic import BaseModel, Field
from typing import List, Optional


class ParameterDoc(BaseModel):
    name: str = Field(description="The parameter name.")
    description: str = Field(description="What the parameter represents.")


class FunctionDoc(BaseModel):
    function_name: str = Field(description="Name of the function.")
    signature: str = Field(description="Full function signature, e.g. 'def foo(a, b)'.")
    description: str = Field(description="Concise description of what the function does.")
    parameters: List[ParameterDoc] = Field(default=[], description="Documentation for each parameter.")
    returns: str = Field(description="Description of the return value.")
    examples: List[str] = Field(default=[], description="Usage examples showing input → output.")
    edge_cases: List[str] = Field(default=[], description="Known edge-case behaviors or caveats.")


class ModuleDoc(BaseModel):
    module_name: str = Field(description="Name of the module (e.g. 'hangman').")
    source_path: str = Field(description="Path to the original source file.")
    summary: str = Field(description="High-level summary of the module's purpose.")
    functions: List[FunctionDoc] = Field(default=[], description="Documentation for each function in the module.")
