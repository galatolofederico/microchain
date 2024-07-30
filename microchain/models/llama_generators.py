import typing as t
from enum import Enum

from microchain.models.openai_generators import TokenTracker
from pydantic import BaseModel


class Llama31SupportedRole(str, Enum):
    system = "system"
    assistant = "assistant"
    user = "user"
    ipython = "ipython"


class Llama31Message(t.TypedDict):
    role: Llama31SupportedRole
    content: str


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int


class ReplicateLlama31ChatGenerator:
    def __init__(
        self,
        *,
        model: str,
        tokenizer_pretrained_model_name_or_path: str,
        api_key: str,
        # Default values set according to their API: https://replicate.com/meta/meta-llama-3.1-405b-instruct
        temperature: float = 0.6,
        top_p: float = 0.9,
        top_k: int = 50,
        max_tokens: int = 1024,
        token_tracker: TokenTracker | None = TokenTracker(),
    ) -> None:
        try:
            from transformers import AutoTokenizer
            from replicate.client import Client
        except ImportError:
            raise ImportError("Please install replicate and transformers using pip install replicate transformers")

        self.model = model
        self.client = Client(api_token=api_key)
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.max_tokens = max_tokens
        self.token_tracker = token_tracker
        self.tokenizer = AutoTokenizer.from_pretrained(
            tokenizer_pretrained_model_name_or_path
        )

    def __call__(
        self, messages: list[Llama31Message], stop: list[str] | None = None
    ) -> str:
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False)
        completion = self.client.predictions.create(
            model=self.model,
            input={
                "prompt": prompt,
                "prompt_template": "{prompt}",  # Force Replicate's API to just use our prompt as-is, otherwise they would use their default formatting which doesn't work for list of messages.
                "stop": stop,
                "top_k": self.top_k,
                "top_p": self.top_p,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
            },
            stream=True,
        )
        output = "".join(str(event) for event in completion.stream()).strip()

        if self.token_tracker:
            self.token_tracker.update_from_usage(
                Usage(
                    prompt_tokens=len(self.tokenizer.apply_chat_template(messages)),
                    completion_tokens=len(self.tokenizer.encode(output)),
                )
            )

        return output

    def print_usage(self) -> None:
        if self.token_tracker:
            print(
                f"Usage: prompt={self.token_tracker.prompt_tokens}, completion={self.token_tracker.completion_tokens}, cost=${self.token_tracker.get_total_cost(self.model):.2f}"
            )
        else:
            print("Token tracker not available")
