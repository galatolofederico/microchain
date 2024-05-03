from microchain.engine.function import Function, FunctionResult
from termcolor import colored

class Agent:
    def __init__(self, llm, engine, on_iteration_end=None):
        self.llm = llm
        self.engine = engine
        self.max_tries = 10
        self.prompt = None
        self.bootstrap = []
        self.do_stop = False
        self.on_iteration_end = on_iteration_end

        self.engine.bind(self)
        self.reset()

    def reset(self):
        self.history = []
        self.do_stop = False

    def execute_command(self, command: str):
        result, output = self.engine.execute(command)
        if result == FunctionResult.ERROR:
            raise Exception(f"Your command ({command}) contains an error. output={output}")

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

    def build_initial_messages(self):
        self.history = [
            dict(
                role="user",
                content=self.prompt
            ),
        ]
        for command in self.bootstrap:
            self.execute_command(command)
            
    def clean_reply(self, reply):
        reply = reply.replace("\_", "_")
        reply = reply.strip()
        reply = reply[:reply.rfind(")")+1]
        return reply

    def stop(self):
        self.do_stop = True

    def step(self):
        result = FunctionResult.ERROR
        temp_messages = []
        tries = 0
        abort = False
        output = ""
        reply = ""
        while result != FunctionResult.SUCCESS:
            tries += 1

            if self.do_stop:
                abort = True
                break

            if tries > self.max_tries:
                print(colored(f"Tried {self.max_tries} times (agent.max_tries) Aborting", "red"))
                abort = True
                break
            
            reply = self.llm(self.history + temp_messages, stop=["\n"])
            reply = self.clean_reply(reply)

            if len(reply) < 2:
                print(colored("Error: empty reply, aborting", "red"))
                abort = True
                break

            print(colored(f">> {reply}", "yellow"))
            
            result, output = self.engine.execute(reply)

            if result == FunctionResult.ERROR:
                print(colored(output, "red"))
                temp_messages.append(dict(
                    role="assistant",
                    content=reply
                ))
                temp_messages.append(dict(
                    role="user",
                    content=output
                ))
            else:
                print(colored(output, "green"))
                break
        
        return dict(
            abort=abort,
            reply=reply,
            output=output,
        )

    def run(self, iterations=10, resume=False):
        if self.prompt is None:
            raise ValueError("You must set a prompt before running the agent")

        if not resume:
            print(colored(f"prompt:\n{self.prompt}", "blue"))
            self.reset()
            self.build_initial_messages()

        print(colored(f"Running {iterations} iterations", "green"))
        for it in range(iterations):
            if self.do_stop:
                break

            step_output = self.step()
            
            if step_output["abort"]:
                break

            self.history.append(dict(
                role="assistant",
                content=step_output["reply"]
            ))
            self.history.append(dict(
                role="user",
                content=step_output["output"]
            ))
            if self.on_iteration_end is not None:
                self.on_iteration_end(self)
            
        print(colored(f"Finished {iterations} iterations", "green"))
