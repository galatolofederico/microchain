from termcolor import colored
from microchain.models.token_tracker import TokenTracker


class OpenAIChatGenerator:
    def __init__(self, *, model, api_key, api_base, temperature=0.9, top_p=1, max_tokens=512, timeout=30, token_tracker=TokenTracker(), enable_langfuse=False):
        if enable_langfuse:
            try:
                from langfuse.openai import openai
            except ImportError:
                raise ImportError("Please install Langfuse and OpenAI python library using pip install langfuse openai")
        else:
            try:
                import openai
            except ImportError:
                raise ImportError("Please install OpenAI python library using pip install openai")
    
        self.model = model
        self.api_key = api_key
        self.api_base = api_base
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.token_tracker = token_tracker
        self.enable_langfuse = enable_langfuse

        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.api_base
        )

        if self.enable_langfuse:
            self.init_langfuse()

    def init_langfuse(self):
        try:
            from langfuse.decorators import observe
        except ImportError:
            raise ImportError("Please install langfuse using pip install langfuse")
        
        self.__call__ = observe(name=self.__class__.__name__)(self.__call__)
    
    def __call__(self, messages, stop=None):
        if self.enable_langfuse:
            from langfuse.openai import openai
        else:
            import openai

        oai_error = openai.error.OpenAIError if hasattr(openai, "error") else openai.OpenAIError
        assert isinstance(messages, list), "messages must be a list of messages https://platform.openai.com/docs/guides/text-generation/chat-completions-api"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
                stop=stop,
                timeout=self.timeout
            )
        except oai_error as e:
            print(colored(f"Error: {e}", "red"))
            return "Error: timeout"

        output = response.choices[0].message.content.strip()

        if self.token_tracker:
            self.token_tracker.update_from_usage(response.usage)

        return output
    
    def print_usage(self):
        if self.token_tracker:
            print(f"Usage: prompt={self.token_tracker.prompt_tokens}, completion={self.token_tracker.completion_tokens}, cost=${self.token_tracker.get_total_cost(self.model):.2f}")
        else:
            print("Token tracker not available")

class OpenAITextGenerator:
    def __init__(self, *, model, api_key, api_base, temperature=0.9, top_p=1, max_tokens=512, enable_langfuse=False):
        if enable_langfuse:
            try:
                from langfuse.openai import openai
            except ImportError:
                raise ImportError("Please install Langfuse and OpenAI python library using pip install langfuse openai")
        else:
            try:
                import openai
            except ImportError:
                raise ImportError("Please install OpenAI python library using pip install openai")
    
        self.model = model
        self.api_key = api_key
        self.api_base = api_base
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.enable_langfuse = enable_langfuse

        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.api_base
        )

        if self.enable_langfuse:
            self.init_langfuse()

    def init_langfuse(self):
        try:
            from langfuse.decorators import observe
        except ImportError:
            raise ImportError("Please install langfuse using pip install langfuse")
        
        self.__call__ = observe(name=self.__class__.__name__)(self.__call__)

    def __call__(self, prompt, stop=None):
        if self.enable_langfuse:
            from langfuse.openai import openai
        else:
            import openai

        oai_error = openai.error.OpenAIError if hasattr(openai, "error") else openai.OpenAIError
        assert isinstance(prompt, str), "prompt must be a string https://platform.openai.com/docs/guides/text-generation/chat-completions-api"

        try:
            response = self.client.completions.create(
                model=self.model,
                prompt=prompt,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
                stop=stop
            )
        except oai_error as e:
            print(colored(f"Error: {e}", "red"))
            return "Error: timeout"

        if "choices" in response:  # vllm
            output = response.choices[0].text.strip()
        elif "content" in response: # llama.cpp
            output = response.content.strip()
        else:
            raise Exception("Unknown output format")
        
        return output
    
