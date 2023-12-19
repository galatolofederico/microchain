import os
import random
from dotenv import load_dotenv   # pip install python-dotenv

from microchain import OpenAITextGenerator, HFChatTemplate, LLM, Function, Engine, Agent
from microchain.functions import Reasoning, Stop

class Sum(Function):
    @property
    def description(self):
        return "Use this function to compute the sum of two numbers"
    
    @property
    def example_args(self):
        return [2, 2]
    
    def __call__(self, a: float, b: float):
        return a + b

class Product(Function):
    @property
    def description(self):
        return "Use this function to compute the product of two numbers"
    
    @property
    def example_args(self):
        return [2, 2]
    
    def __call__(self, a: float, b: float):
        return a * b

load_dotenv()

generator = OpenAITextGenerator(
    model=os.environ["MODEL_NAME"],
    api_key=os.environ["API_KEY"],
    api_base=os.environ["API_BASE"],
    temperature=0.7
)

template = HFChatTemplate(os.environ["TEMPLATE_NAME"])
llm = LLM(generator=generator, templates=[template])

engine = Engine()
engine.register(Reasoning())
engine.register(Stop())
engine.register(Sum())
engine.register(Product())

agent = Agent(llm=llm, engine=engine)
agent.prompt = f"""Act as a calculator. You can use the following functions:

{engine.help}

Only output valid Python function calls.

How much is (2*4 + 3)*5?
"""

agent.bootstrap = [
    'Reasoning("I need to reason step-by-step")',
]
agent.run()