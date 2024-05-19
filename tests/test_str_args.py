import unittest
from microchain import Engine, Function, Agent
from unittest.mock import patch
import io
import sys

class StrArgs(Function):
    @property
    def description(self):
        return "This function returns a + len(b)"
    
    @property
    def example_args(self):
        return [2, "test"]
    
    def __call__(self, a: float, b: str):
        return a + len(b)
    
class LLM:
        def __call__(self, prompt, stop=None):
            return ""
    
class TestAgent(unittest.TestCase):
    
    def test_prompt_not_present(self):
        engine = Engine()
        f = StrArgs()
        engine.register(f)
        llm = object()
        agent = Agent(llm=llm, engine=engine)
        
        self.assertEqual(f.example, "StrArgs(a=2, b='test')")

if __name__ == '__main__':
    unittest.main()