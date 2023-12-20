from microchain.engine.function import Function, FunctionResult
from termcolor import colored

class Agent:
    def __init__(self, llm, engine):
        self.llm = llm
        self.engine = engine
        self.max_tries = 10
        self.prompt = None
        self.bootstrap = []
        self.do_stop = False

        self.engine.bind(self)
        self.reset()

    def reset(self):
        self.history = []
        self.do_stop = False

    def build_initial_messages(self):
        self.history = [
            dict(
                role="user",
                content=self.prompt
            ),
        ]
        for command in self.bootstrap:
            result, output = self.engine.execute(command)
            if result == FunctionResult.ERROR:
                raise Exception(f"Your bootstrap commands contain an error. output={output}")

            print(colored(f">> {command}", "blue"))
            print(colored(f"{output}", "green"))

            self.history.append(dict(
                role="assistant",
                content=command
            ))
            self.history.append(dict(
                role="user",
                content=output
            ))
            
    def clean_reply(self, reply):
        reply = reply.replace("\_", "_")
        reply = reply.strip()
        reply = reply[:reply.rfind(")")+1]
        return reply

    def stop(self):
        self.do_stop = True

    def run(self, iterations=10):
        if self.prompt is None:
            raise ValueError("You must set a prompt before running the agent")

        print(colored(f"prompt:\n{self.prompt}", "blue"))
        print(colored(f"Running {iterations} iterations", "green"))

        self.reset()
        self.build_initial_messages()

        for it in range(iterations):
            if self.do_stop:
                break
            state = FunctionResult.ERROR
            temp_messages = []
            tries = 0
            abort = False
            while state != FunctionResult.SUCCESS:
                if self.do_stop:
                    abort = True
                    break
                if tries > self.max_tries:
                    print(colored(f"Tried {self.max_tries} times (agent.max_tries) Aborting", "red"))
                    abort = True
                    break
                tries += 1
                reply = self.llm(self.history + temp_messages, stop=["\n"])
                reply = self.clean_reply(reply)
                if len(reply) < 2:
                    print(colored("Error: empty reply, aborting", "red"))
                    abort = True
                    break

                print(colored(f">> {reply}", "yellow"))
                
                state, out = self.engine.execute(reply)

                if state == FunctionResult.ERROR:
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
            self.history.append(dict(
                role="assistant",
                content=reply
            ))
            self.history.append(dict(
                role="user",
                content=out
            ))
            
        print(colored(f"Finished {iterations} iterations", "green"))
