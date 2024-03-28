import unittest
from microchain import Engine, Function, FunctionResult

class Sum(Function):
    @property
    def description(self):
        return "Use this function to compute the sum of two numbers"
    
    @property
    def example_args(self):
        return [2, 2]
    
    def __call__(self, a: float, b: float):
        return a + b


class TestEngine(unittest.TestCase):
    
    def test_engine_binded(self):
        engine = Engine()
        self.assertRaisesRegex(ValueError,"You must bind the engine to an agent before executing commands", engine.execute, "Sum(a=2, b=2)")

    def test_help_called(self):
        engine = Engine()
        engine.agent=object()   # to bind the engine to an agent
        self.assertRaisesRegex(ValueError,"You never accessed the help property. Building a prompt without including the help string is a very bad idea.", engine.execute, "Sum(a=2, b=2)")

    def test_syntax_error(self):
        engine = Engine()
        engine.agent=object()   
        engine.help_called = True   # to access the help property
        self.assertEqual((FunctionResult.ERROR, "Error: syntax error in command sum(,). Please try again."), engine.execute("sum(,)"))

    def test_not_function_call(self):
        engine = Engine()
        engine.agent=object()   
        engine.help_called = True   # to access the help property
        self.assertEqual((FunctionResult.ERROR, "Error: the command sum must be a function call. Please try again."), engine.execute("sum"))

    def test_constant_arguments(self):
        engine = Engine()
        engine.agent=object()   
        engine.help_called = True
        self.assertEqual((FunctionResult.ERROR, "Error: the command Sum(2*4, 2) must be a function call, you cannot use variables. Please try again."), engine.execute("Sum(2*4, 2)"))

    def test_constant_keyword_arguments(self):
        engine = Engine()
        engine.agent=object()   
        engine.help_called = True
        self.assertEqual((FunctionResult.ERROR, "Error: the command Sum(a=2*4, b=2) must be a function call, you cannot use variables. Please try again."), engine.execute("Sum(a=2*4, b=2)"))

    def test_function_not_registered(self):
        engine = Engine()
        engine.agent=object()   
        engine.help_called = True
        self.assertEqual((FunctionResult.ERROR, "Error: unknown command Sum(2, 2). Please try again."), engine.execute("Sum(2, 2)"))

    def test_function_too_many_arguments(self):
        engine = Engine()
        engine.agent=object()   
        engine.help_called = True
        engine.register(Sum())
        self.assertEqual((FunctionResult.ERROR, "Error: wrong format. Use Sum(a: float, b: float). Example: Sum(a=2, b=2). Please try again."), engine.execute("Sum(2, 2, 2)"))

    def test_function_not_enough_arguments(self):
        engine = Engine()
        engine.agent=object()   
        engine.help_called = True
        engine.register(Sum())
        self.assertEqual((FunctionResult.ERROR, "Error: wrong format. Use Sum(a: float, b: float). Example: Sum(a=2, b=2). Please try again."), engine.execute("Sum(2)"))

    def test_correct_function_call(self):
        engine = Engine()
        engine.agent=object()   
        engine.help_called = True
        engine.register(Sum())
        self.assertEqual((FunctionResult.SUCCESS, "4"), engine.execute("Sum(2,2)"))


if __name__ == '__main__':
    unittest.main()