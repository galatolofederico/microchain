class LLM:
    def __init__(self, *, generator, templates=[]):
        if not isinstance(templates, list):
            templates = [templates]
        
        self.generator = generator
        self.templates = templates
    
    def __call__(self, prompt, stop=None):
        for template in self.templates:
            prompt = template(prompt)

        return self.generator(prompt, stop=stop)