from microchain.engine.function import Function, FunctionResult
from termcolor import colored

class Agent:
    def __init__(self, llm, engine):
        self.llm = llm
        self.engine = engine
        self.max_tries = 10
        self.prompt = None
        self.bootstrap = []

    def build_initial_messages(self):
        history = [
            dict(
                role="user",
                content=self.prompt
            ),
        ]
        for command in self.bootstrap:
            result, output = self.engine.execute(command)
            if result == FunctionResult.ERROR:
                raise Exception(f"Your bootstrap commands contain an error. output={output}")
            
            history.append(dict(
                role="assistant",
                content=command
            ))
            history.append(dict(
                role="user",
                content=output
            ))
    
    def clean_reply(reply):
        reply = reply.replace("\_", "_")
        reply = reply.strip()
        reply = reply[:reply.rfind(")")+1]
        return reply

    def run(self, iterations=10):
        if self.prompt is None:
            raise ValueError("You must set a prompt before running the agent")
        
        history = self.build_initial_messages()

        print("--------------------")
        print(colored("prompt:\n", history[0]["content"], "blue"))
        print(colored(f"Running {iterations} iterations", "green"))

        for it in range(iterations):
            state = FunctionResult.ERROR
            temp_messages = []
            tries = 0
            abort = False
            while state != FunctionResult.SUCCESS:
                if tries > self.max_tries:
                    print(colored(f"Tried {self.max_tries} times (agent.max_tries) Aborting", "red"))
                    abort = True
                    break
                tries += 1
                reply = self.clean_reply(self.llm(history + temp_messages, stop=["\n"]))
                if len(reply) < 2:
                    print(colored("Error: empty reply, aborting", "red"))
                    abort = True
                    break

                print(colored(f">> {reply}", "yellow"))
                
                state, out = self.engine.execute(reply)

                temp_messages = []
                if state == FunctionResult:
                    print(colored(out, "red"))
                    temp_messages.append(dict(
                        role="assistant",
                        content=reply
                    ))
                    temp_messages.append(dict(
                        role="user",
                        content=out
                    ))
            
            if abort:
                break

            print(colored(out, "green"))
            history.append(dict(
                role="assistant",
                content=reply
            ))
            history.append(dict(
                role="user",
                content=out
            ))
            

        print(colored(f"Finished {iterations} iterations", "green"))
        print("--------------------")