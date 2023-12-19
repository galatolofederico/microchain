import enum
import inspect

EXAMPLE = """
class PlaceMark(Function):
    @property
    def description(self):
        return "Place a mark on the board"

    @property
    def example_args(self):
        return [0, 0]

    def __call__(self, /, x: int, y: int):
        print(f"Placing mark at {x} {y}")
"""

class FunctionResult(enum.Enum):
    SUCCESS = 0
    ERROR = 1

class Function:
    def __init__(self):
        self.call_signature = inspect.signature(self.__call__)        
        self.call_parameters = []
        for name, parameter in self.call_signature.parameters.items():
            if parameter.annotation == inspect._empty:
                raise ValueError(f"Parameter {name} must have an annotation")
            
            self.call_parameters.append(dict(
                name=name,
                annotation=parameter.annotation
            ))

    @property
    def example(self):
        if not isinstance(self.example_args, list):
            raise ValueError("example_args must be a list")
        
        bound = self.call_signature.bind(*self.example_args)
        
        return f"{type(self).__name__}({', '.join([f'{name}={value}' for name, value in bound.arguments.items()])})"
    
    @property
    def signature(self):
        fname = type(self).__name__
        arguments = [f"{parameter['name']}: {parameter['annotation'].__name__}" for parameter in self.call_parameters]
        return f"{fname}({', '.join(arguments)})"

    @property
    def help(self):
        return f"{self.signature}\n{self.description}.\nExample: {self.example}\n"

    @property
    def error(self):
        return f"Error: wrong format. Use {self.signature}. Example: {self.example}"
    

    def __call__(self, command):
        raise NotImplementedError
    
