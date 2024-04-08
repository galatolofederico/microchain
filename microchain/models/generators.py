from termcolor import colored

class OpenAIChatGenerator:
    def __init__(self, *, model, api_key, api_base, temperature=0.9, top_p=1, max_tokens=512, timeout=30):
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

        return output
    


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
    