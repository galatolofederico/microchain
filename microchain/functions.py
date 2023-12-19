from microchain import Function

class Reasoning(Function):
    @property
    def description(self):
        return "Use this function for your internal reasoning"

    @property
    def example_args(self):
        return ["The next step to take is..."]

    def __call__(self, reasoning: str):
        return f"The reasoning has been recorded"
    
class Stop(Function):
    @property
    def description(self):
        return "Use this function to stop the program"

    @property
    def example_args(self):
        return []

    def __call__(self):
        self.engine.stop()
        return "The program has been stopped"
