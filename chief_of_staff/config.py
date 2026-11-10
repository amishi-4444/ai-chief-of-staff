"""LLM provider setup. Default = OpenAI. Set LLM_BASE_URL to use any OpenAI-compatible
provider (Gemini, Groq, Ollama...). Call configure() once at startup."""
import os
from openai import AsyncOpenAI
from agents import set_default_openai_api, set_default_openai_client, set_tracing_disabled

CUSTOM_PROVIDER = bool(os.getenv("LLM_BASE_URL"))
USE_WEB_SEARCH = not CUSTOM_PROVIDER  # hosted WebSearchTool is OpenAI-only


def configure() -> None:
    if CUSTOM_PROVIDER:
        client = AsyncOpenAI(base_url=os.environ["LLM_BASE_URL"], api_key=os.getenv("LLM_API_KEY", "none"))
        set_default_openai_client(client, use_for_tracing=False)
        set_default_openai_api("chat_completions")
        set_tracing_disabled(True)
