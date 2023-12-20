# microchain

function calling-based LLM agents. Just that, no bloat.

## Installation

```
pip install microchain-python
```

## Define LLM and template

```python
from microchain import OpenAITextGenerator, HFChatTemplate, LLM

generator = OpenAITextGenerator(
    model=MODEL_NAME,
    api_key=API_KEY,
    api_base=API_BASE,
    temperature=0.7
)

template = HFChatTemplate(CHAT_TEMPLATE)
llm = LLM(generator=generator, templates=[template])
```

Use `HFChatTemplate(template)` to use `tokenizer.apply_chat_template` from `huggingface`.

You can also use `VicunaTemplate()` for a classic vicuna-style prompt.

To use ChatGPT APIs you don't need to apply a template:

```python
from microchain import OpenAIChatGenerator, LLM

generator = OpenAIChatGenerator(
    model="gpt-3.5-turbo",
    api_key=API_KEY,
    api_base="https://api.openai.com/v1",
    temperature=0.7
)

llm = LLM(generator=generator)
```

## Define LLM functions

Define **LLM callable functions** as plain Python objects. Use **type annotations** to instruct the LLM to use the correct types.

```python
from microchain import Function

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

print(Sum().help)
'''
Sum(a: float, b: float)
This function sums two numbers.
Example: Sum(a=2, b=2)
'''

print(Product().help)
'''
Product(a: float, b: float)
Use this function to compute the product of two numbers.
Example: Product(a=2, b=2)
'''
```

## Define a LLM Agent

Register your functions with an `Engine()` using the `register()` function.

Create an `Agent()` using the `llm` and the execution `engine`. 

Define a prompt for the LLM and include the functions documentation using `engine.help()`. 

It's always a good idea to bootstrap the LLM with examples of function calls. Do this by setting `engine.bootstrap = [...]` with a list of function calls to run and prepend their results to the chat history.

```python
from microchain import Agent, Engine
from microchain.functions import Reasoning, Stop

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
```

Running it will output something like:

```
prompt:
Act as a calculator. You can use the following functions:

Reasoning(reasoning: str)
Use this function for your internal reasoning.
Example: Reasoning(reasoning=The next step to take is...)

Stop()
Use this function to stop the program.
Example: Stop()

Sum(a: float, b: float)
Use this function to compute the sum of two numbers.
Example: Sum(a=2, b=2)

Product(a: float, b: float)
Use this function to compute the product of two numbers.
Example: Product(a=2, b=2)


Only output valid Python function calls.

How much is (2*4 + 3)*5?

Running 10 iterations
>> Reasoning("I need to reason step-by-step")
The reasoning has been recorded
>> Reasoning("First, calculate the product of 2 and 4")
The reasoning has been recorded
>> Product(a=2, b=4)
8
>> Reasoning("Then, add 3 to the product of 2 and 4")
The reasoning has been recorded
>> Sum(a=8, b=3)
11
>> Reasoning("Lastly, multiply the sum by 5")
The reasoning has been recorded
>> Product(a=11, b=5)
55
>> Reasoning("So, the result of (2*4 + 3)*5 is 55")
The reasoning has been recorded
>> Stop()
The program has been stopped
```

You can find more examples [here](./examples/)