# microagent

Function-calling based LLM agents. Just that, no bloat.

## Installation

```
pip install microagent
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

## Define LLM functions

Define **LLM callable functions** as basic Python objects, use **type annotations** to instruct the LLM to use the correct types.

```python
from microchain import Function

class Sum(Function):
    @property
    def description(self):
        return "This function sums two numbers"
    
    @property
    def example_args(self):
        return [2, 2]
    
    def __call__(self, a:int, b:int):
        return a + b

print(Sum().help)
'''
Sum(a: int, b: int)
This function sums two numbers.
Example: Sum(a=2, b=2)
'''
```

## Define a LLM Agent

```python
from microchain import Engine

engine = Engine()
engine.register(Sum())

agent = Agent(llm=llm, engine=engine)
agent.prompt = f"""Act as a calculator. You can use the following functions:

{engine.help}

Only output valid python function calls.

How much is 43 + 27?
"""
agent.run()
```


## Example

A tic-tac-toe playing agent

```python
def check_win(board):
    if board.has_won(1):
        return ". You won!"
    elif board.has_won(2):
        return ". You lost!"
    return ""

class State(Function):
    @property
    def description(self):
        return "Use this function to get the state of the board"

    @property
    def example_args(self):
        return []

    def __call__(self):
        return str(self.state["board"]) + check_win(self.state["board"])

class PlaceMark(Function):
    @property
    def description(self):
        return "Use this function to place a mark on the board. x represents the row and y the column. Starts at 0"

    @property
    def example_args(self):
        return [1, 1]

    def __call__(self, x: int, y: int):
        if (x, y) not in self.state["board"].possible_moves():
            return f"Error: the move {x} {y} is not valid"
        
        try:
            self.state["board"].push((x, y))
        except Exception as e:
            return f"Error: {e}"

        if len(self.state["board"].possible_moves()) > 0:
            move = random.choice(self.state["board"].possible_moves())
            self.state["board"].push(move)
            return f"Placed mark at {x} {y}. Your opponent placed a mark at {move[0]} {move[1]}." + check_win(self.state["board"])

        self.engine.stop()
        return f"Placed mark at {x} {y}." + check_win(self.state["board"]) + ". The game is over"

class Reasoning(Function):
    @property
    def description(self):
        return "Use this function for your internal reasoning"

    @property
    def example_args(self):
        return ["I need to place a mark at 1 1"]

    def __call__(self, reasoning: str):
        return f"The reasoning has been recorded"


class Stop(Function):
    @property
    def description(self):
        return "Use this function to stop the game"

    @property
    def example_args(self):
        return []

    def __call__(self):
        self.engine.stop()


engine = Engine(state=dict(board=Board()))
engine.register(State())
engine.register(PlaceMark())
engine.register(Reasoning())

agent = Agent(llm=llm, engine=engine)
agent.prompt = f"""Act as a tic tac toe playing AI. You can use the following functions:

{engine.help}

You are playing with X.
Take a deep breath and work on this problem step-by-step.
Always check the state of the board before placing a mark.
Only output valid python function calls.
"""
agent.bootstrap = [
    'Reasoning("I need to check the state of the board")',
    'State()',
]
agent.run(iterations=30)

'''
--------------------
prompt:
Act as a tic tac toe playing AI. You can use the following functions:

State()
Use this function to get the state of the board.
Example: State()

PlaceMark(x: int, y: int)
Use this function to place a mark on the board. x represents the row and y the column. Starts at 0.
Example: PlaceMark(x=1, y=1)

Reasoning(reasoning: str)
Use this function for your internal reasoning.
Example: Reasoning(reasoning=I need to place a mark at 1 1)


You are playing with X.
Take a deep breath and work on this problem step-by-step.
Always check the state of the board before placing a mark.
Only output valid python function calls.

Running 30 iterations
>> Reasoning("I need to check the state of the board")
The reasoning has been recorded
>> State()
   |   |   
-----------
   |   |   
-----------
   |   |   
>> Reasoning("The board is empty, I can place my mark anywhere.")
The reasoning has been recorded
>> PlaceMark(x=1, y=1)
Placed mark at 1 1. Your opponent placed a mark at 0 1.
>> Reasoning("My opponent has placed their mark at 0 1, I will block them from getting three in a row.")
The reasoning has been recorded
>> State()
   |   |   
-----------
 O | X |   
-----------
   |   |   
>> PlaceMark(x=1, y=0)
Placed mark at 1 0. Your opponent placed a mark at 2 1.
>> Reasoning("My opponent has placed their mark at 2 1, I will block them from getting three in a row.")
The reasoning has been recorded
>> State()
   | X |   
-----------
 O | X | O 
-----------
   |   |   
>> PlaceMark(x=0, y=0)
Placed mark at 0 0. Your opponent placed a mark at 1 2.
>> Reasoning("My opponent has placed their mark at 1 2, I will block them from getting three in a row.")
The reasoning has been recorded
>> State()
 X | X |   
-----------
 O | X | O 
-----------
   | O |   
>> PlaceMark(x=2, y=2)
Placed mark at 2 2. Your opponent placed a mark at 2 0.. You won!
>> Reasoning("My opponent has placed their mark at 2 0, but I have already won the game!")
The reasoning has been recorded
>> State()
 X | X | O 
-----------
 O | X | O 
-----------
   | O | X . You won!
>> Reasoning("I have won the game!")
The reasoning has been recorded
'''
```