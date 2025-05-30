from typing import Optional
from openai import OpenAI

SMALL_MODEL = "gpt-4.1-nano"
MEDIUM_MODEL = "gpt-4.1-mini"
LARGE_MODEL = "gpt-4.1"


class OpenAIClient:
    _client: Optional[OpenAI] = None

    def __new__(cls, *args, **kwargs):
        if cls._client:
            return cls._client
        cls._client = OpenAI(
            base_url="https://api.metisai.ir/openai/v1"
        )
        return cls._client
