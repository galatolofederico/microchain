import unittest
from microchain import Engine, Function, Agent
from unittest.mock import patch
import io
import sys

class Sum(Function):
    @property
    def description(self):
        return "Use this function to compute the sum of two numbers"
    
    @property
    def example_args(self):
        return [2, 2]
    
    def __call__(self, a: float, b: float):
        return a + b
    
class LLM:
        def __call__(self, prompt, stop=None):
            return ""
    
class TestAgent(unittest.TestCase):
    
    def test_prompt_not_present(self):
        engine = Engine()
        llm = object()
        agent = Agent(llm=llm, engine=engine)
        
        self.assertRaisesRegex(ValueError,"You must set a prompt before running the agent", agent.run)

    def test_error_in_bootstrap(self):
        engine = Engine()
        engine.register(Sum())
        engine.agent=object()
        engine.help_called = True
        llm = object()
        agent = Agent(llm=llm, engine=engine)
        
        agent.prompt=""
        agent.bootstrap = [
            'Sum(a=2*2, b=2)'
        ]
        self.assertRaisesRegex(Exception, r".*Your command \(Sum\(a=2\*2, b=2\)\) contains an error. output=Error: the command Sum\(a=2\*2, b=2\) must be a function call, you cannot use variables\. Please try again\..*", agent.run, 1)

    def test_step_empty_reply(self):
        engine = Engine()
        engine.register(Sum())
        engine.agent=object()
        engine.help_called = True
        llm = LLM()
        agent = Agent(llm=llm, engine=engine)
        
        agent.prompt=""
        agent.bootstrap = [
            'Sum(a=2, b=2)'
        ]
        out, err = io.StringIO(), io.StringIO()
        with patch.multiple(sys, stdout=out, stderr=err):
            agent.run()

        assert "Error: empty reply, aborting\n" in out.getvalue()

    def test_exceeded_max_tries(self):
        engine = Engine()
        engine.register(Sum())
        engine.agent=object()
        engine.help_called = True
        llm = LLM()
        agent = Agent(llm=llm, engine=engine)
        
        agent.prompt=""
        agent.bootstrap = [
            'Sum(a=2, b=2)'
        ]
        agent.max_tries = -1
        out, err = io.StringIO(), io.StringIO()
        with patch.multiple(sys, stdout=out, stderr=err):
            agent.run()

        assert "Tried -1 times (agent.max_tries) Aborting" in out.getvalue()
    

if __name__ == '__main__':
    unittest.main()