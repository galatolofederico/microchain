import ast

from microchain.engine.function import Function, FunctionResult

class Engine:
    def __init__(self, state=dict()):
        self.state = state
        self.functions = dict()
        self.help_called = False
        self.agent = None
    
    def register(self, function):
        self.functions[function.name] = function
        function.bind(state=self.state, engine=self)

    def bind(self, agent):
        self.agent = agent

    def stop(self):
        if self.agent is None:
            raise ValueError("You must bind the engine to an agent before stopping")
        self.agent.stop()

    def execute(self, command):
        if self.agent is None:
            raise ValueError("You must bind the engine to an agent before executing commands")
        if not self.help_called:
            raise ValueError("You never accessed the help property. Building a prompt without including the help string is a very bad idea.")
        try:
            tree = ast.parse(command)
        except SyntaxError:
            return FunctionResult.ERROR, f"Error: syntax error in command {command}. Please try again."
        
        if len(tree.body) != 1:
            return FunctionResult.ERROR, f"Error: unknown command {command}. Please try again."

        if not isinstance(tree.body[0], ast.Expr):
            return FunctionResult.ERROR, f"Error: unknown command {command}. Please try again."

        if not isinstance(tree.body[0].value, ast.Call):
            return FunctionResult.ERROR, f"Error: the command {command} must be a function call. Please try again."
        
        if not isinstance(tree.body[0].value.func, ast.Name):
            return FunctionResult.ERROR, f"Error: the command {command} must be a function call. Please try again."

        function_name = tree.body[0].value.func.id
        function_args = tree.body[0].value.args
        function_kwargs = tree.body[0].value.keywords

        for arg in function_args:
            if not isinstance(arg, ast.Constant):
                return FunctionResult.ERROR, f"Error: the command {command} must be a function call, you cannot use variables. Please try again."

        for kwarg in function_kwargs:
            if not isinstance(kwarg, ast.keyword):
                return FunctionResult.ERROR, f"Error: the command {command} must be a function call, you cannot use variables. Please try again."
            if not isinstance(kwarg.value, ast.Constant):
                return FunctionResult.ERROR, f"Error: the command {command} must be a function call, you cannot use variables. Please try again."

        function_args = [arg.value for arg in function_args]
        function_kwargs = {kwarg.arg: kwarg.value.value for kwarg in function_kwargs}

        if function_name not in self.functions:
            return FunctionResult.ERROR, f"Error: unknown command {command}. Please try again."
        
        if len(function_args) + len(function_kwargs) != len(self.functions[function_name].call_parameters):
            return FunctionResult.ERROR, self.functions[function_name].error

        return self.functions[function_name].safe_call(args=function_args, kwargs=function_kwargs)   
    
    @property
    def help(self):
        self.help_called = True
        return "\n".join([f.help for f in self.functions.values()])
