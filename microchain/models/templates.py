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