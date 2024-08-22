import enum
import inspect
import traceback
from termcolor import colored

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
        self.state = None
        self.engine = None
    
    def bind(self, *, state, engine):
        self.state = state
        self.engine = engine
        if self.engine.agent is not None and getattr(self.engine.agent, "enable_langfuse", False):
            self.init_langfuse()

    def init_langfuse(self):
        try:
            from langfuse.decorators import observe
        except ImportError:
            raise ImportError("Please install langfuse using pip install langfuse")
        
        self.__call__ = observe(name=self.name)(self.__call__)

    @property
    def name(self):
        return type(self).__name__

    @property
    def example(self):
        if not isinstance(self.example_args, list):
            raise ValueError("example_args must be a list")
        if len(self.example_args) != len(self.call_parameters):
            raise ValueError(f"example_args must have the same length as call_parameters ({len(self.call_parameters)})")

        bound = self.call_signature.bind(*self.example_args)
        return f"{self.name}({', '.join([f'{name}={repr(value)}' for name, value in bound.arguments.items()])})"
    
    @property
    def signature(self):
        arguments = [f"{parameter['name']}: {parameter['annotation'].__name__}" for parameter in self.call_parameters]
        return f"{self.name}({', '.join(arguments)})"

    @property
    def help(self):
        return f"{self.signature}\n{self.description}.\nExample: {self.example}\n"

    @property
    def error(self):
        return f"Error: wrong format. Use {self.signature}. Example: {self.example}. Please try again."

    def check_bind(self):
        if self.state is None:
            raise ValueError("You must register the function to an Engine")

    def safe_call(self, args, kwargs):
        self.check_bind()
        try:
            return FunctionResult.SUCCESS, str(self.__call__(*args, **kwargs))
        except Exception as e:
            stacktrace = ''.join(traceback.TracebackException.from_exception(e).format())
            print(colored(f"Exception in Function call {e}", "red"))
            print(colored(stacktrace, "red"))

            if type(e) in [TypeError, SyntaxError]:
                # Catch remaining errors from a bad call
                return FunctionResult.ERROR, self.error
            else:
                # Return the stacktrace of the error from inside the function
                return FunctionResult.ERROR, f"Error inside function call: {stacktrace}"

    def __call__(self, command):
        raise NotImplementedError
    
