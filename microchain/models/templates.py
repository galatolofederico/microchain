class HFChatTemplate:
    def __init__(self, template):
        try:
            import transformers
        except ImportError:
            raise ImportError("Please install transformers python library using pip install transformers")
        
        try:
            import jinja2
        except ImportError:
            raise ImportError("Please install jinja2 python library using pip install jinja2")

        self.tokenizer = transformers.AutoTokenizer.from_pretrained(template)

    def __call__(self, prompt):
        return self.tokenizer.apply_chat_template(prompt, tokenize=False, add_generation_prompt=True)

class VicunaTemplate:
    def __init__(self, user="User", assistant="Assistant", system_prompt=None):
        self.user = user
        self.assistant = assistant
        self.system_prompt = system_prompt
    
    def __call__(self, prompt):
        ret = f"{self.system_prompt}\n\n" if self.system_prompt else f""
        for message in prompt:
            if message["role"] == "user":
                ret += f"{self.user}: {message['content']}\n"
            elif message["role"] == "assistant":
                ret += f"{self.assistant}: {message['content']}\n"
            else:
                raise ValueError(f"Unknown role {message['role']}")
        
        if prompt[-1]["role"] == "user":
            ret += f"{self.assistant}:"
        else:
            raise ValueError(f"Last message should be from user")
        
        return ret