import os
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential
from dotenv import load_dotenv

load_dotenv()

credential = AzureCliCredential()

client = AzureOpenAIChatClient(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    deployment_name=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    api_version=os.environ["AZURE_OPENAI_API_VERSION"],
)