import os
import random
from dotenv import load_dotenv   # pip install python-dotenv
from tictactoe import Board      # pip install python-tictactoe

from microchain import OpenAITextGenerator, HFChatTemplate, LLM, Function, Engine, Agent

load_dotenv()

generator = OpenAITextGenerator(
    model=os.environ["MODEL_NAME"],
    api_key=os.environ["API_KEY"],
    api_base=os.environ["API_BASE"],
    temperature=0.7
)

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

template = HFChatTemplate(os.environ["TEMPLATE_NAME"])
llm = LLM(generator=generator, templates=[template])

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