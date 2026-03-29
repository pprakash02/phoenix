# services/llm_service.py
"""Dynamic LLM client factory supporting multiple Azure AI Foundry deployments."""

import os
from dotenv import load_dotenv
from agent_framework.azure import AzureOpenAIChatClient

load_dotenv()

# Model registry: maps UI model names to .env variable prefixes
# Users configure each model with:
#   {PREFIX}_ENDPOINT, {PREFIX}_API_KEY, {PREFIX}_DEPLOYMENT_NAME, {PREFIX}_API_VERSION
MODEL_REGISTRY = {
    "gpt-4o": {
        "prefix": "AZURE_OPENAI",
        "display_name": "GPT-4o",
        "description": "OpenAI's flagship model for complex reasoning and code generation",
    },
    "gpt-oss-120b": {
        "prefix": "AZURE_OPENAI",
        "display_name": "GPT OSS 120B",
        "description": "Open-source 120B parameter model via Azure",
    },
}

# Cache instantiated clients
_client_cache: dict[str, AzureOpenAIChatClient] = {}


def get_available_models() -> list[dict]:
    """Return list of models that have valid .env configuration."""
    available = []
    for model_id, info in MODEL_REGISTRY.items():
        prefix = info["prefix"]
        endpoint = os.environ.get(f"{prefix}_ENDPOINT")
        api_key = os.environ.get(f"{prefix}_API_KEY")
        if endpoint and api_key:
            available.append({
                "id": model_id,
                "name": info["display_name"],
                "description": info["description"],
                "configured": True,
            })
        else:
            available.append({
                "id": model_id,
                "name": info["display_name"],
                "description": info["description"],
                "configured": False,
            })
    return available


def get_client(model_name: str = None) -> AzureOpenAIChatClient:
    """
    Get an AzureOpenAIChatClient for the specified model.
    Falls back to the default AZURE_OPENAI config if the model-specific config is missing.
    """
    if model_name is None:
        model_name = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")

    # Return cached client if available
    if model_name in _client_cache:
        return _client_cache[model_name]

    info = MODEL_REGISTRY.get(model_name)
    if info:
        prefix = info["prefix"]
    else:
        prefix = "AZURE_OPENAI"

    endpoint = os.environ.get(f"{prefix}_ENDPOINT", os.environ.get("AZURE_OPENAI_ENDPOINT"))
    api_key = os.environ.get(f"{prefix}_API_KEY", os.environ.get("AZURE_OPENAI_API_KEY"))
    deployment = os.environ.get(f"{prefix}_DEPLOYMENT_NAME", os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"))
    api_version = os.environ.get(f"{prefix}_API_VERSION", os.environ.get("AZURE_OPENAI_API_VERSION", "2024-10-21"))

    if not endpoint or not api_key:
        raise ValueError(
            f"Missing Azure configuration for model '{model_name}'. "
            f"Set {prefix}_ENDPOINT and {prefix}_API_KEY in your .env file."
        )

    client = AzureOpenAIChatClient(
        endpoint=endpoint,
        api_key=api_key,
        deployment_name=deployment,
        api_version=api_version,
    )

    _client_cache[model_name] = client
    return client


def clear_cache():
    """Clear the client cache (useful when .env changes)."""
    _client_cache.clear()
