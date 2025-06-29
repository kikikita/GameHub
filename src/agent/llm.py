"""Utility functions for working with the language model."""

import asyncio
import logging

from google.api_core.exceptions import DeadlineExceeded
from langchain_google_genai import ChatGoogleGenerativeAI

from config import settings
from services.google import ApiKeyPool

logger = logging.getLogger(__name__)

_pool = ApiKeyPool()
MODEL_NAME = "gemini-2.5-flash-preview-05-20"


def _get_api_key() -> str:
    """Return an API key using round-robin selection in a thread-safe way."""
    return _pool.get_key_sync()


def create_llm(
    temperature: float = settings.temperature,
    top_p: float = settings.top_p,
) -> ChatGoogleGenerativeAI:
    """Create a standard LLM instance."""
    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        google_api_key=_get_api_key(),
        temperature=temperature,
        top_p=top_p,
        thinking_budget=1024,
        timeout=settings.request_timeout,
        max_retries=3,
    )
    return llm
    
    
def create_light_llm(temperature: float = settings.temperature, top_p: float = settings.top_p):
    """Create a light LLM instance with a shorter timeout."""
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=_get_api_key(),
        temperature=temperature,
        top_p=top_p,
        timeout=settings.request_timeout,
        max_retries=3,
    )
    return llm


def create_precise_llm() -> ChatGoogleGenerativeAI:
    """Return an LLM tuned for deterministic output."""
    return create_llm(temperature=0, top_p=1)
