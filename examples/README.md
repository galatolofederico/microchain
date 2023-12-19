# microchain/examples

## Calculator

Example output of [calcualtor.py](./calculator.py)

```

```

## Tic-Tac-Toe

Example output of [tictactoe.py](tictactoe.py)

```
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
```