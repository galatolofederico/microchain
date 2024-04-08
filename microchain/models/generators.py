from termcolor import colored

class TokenTracker:
    def __init__(self):
        self.prompt_tokens = 0
        self.completion_tokens = 0

    def update_from_usage(self, usage):
        self.prompt_tokens += usage.prompt_tokens
        self.completion_tokens += usage.completion_tokens

    def get_total_cost(self, model):
        # From https://openai.com/pricing
        if model in ["gpt-4-0125-preview", "gpt-4-1106-preview", "gpt-4-turbo-preview"]:
            costs = {"prompt": 1e-05, "completion": 3e-05}
        elif model == "gpt-3.5-turbo-0125":
            costs = {"prompt": 5e-07, "completion": 1.5e-06}
        else:
            print(f"Unsupported {model}")
            return 0

        return self.prompt_tokens * costs["prompt"] + self.completion_tokens * costs["completion"]



class OpenAIChatGenerator:
    def __init__(self, *, model, api_key, api_base, temperature=0.9, top_p=1, max_tokens=512, timeout=30, token_tracker=TokenTracker()):
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

        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.api_base
        )
    
    def __call__(self, messages, stop=None):
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
    def __init__(self, *, model, api_key, api_base, temperature=0.9, top_p=1, max_tokens=512):
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

        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.api_base
        )
    
    def __call__(self, prompt, stop=None):
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
        
        output = response.choices[0].text.strip()

        return output
    