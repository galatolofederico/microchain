from dataclasses import dataclass
from termcolor import colored

from microchain.engine.function import FunctionResult


@dataclass
class StepOutput:
    abort: bool
    reply: str
    output: str
    result: FunctionResult

class Agent:
    def __init__(self, llm, engine, on_iteration_start=None, on_iteration_step=None, on_iteration_end=None, stop_list=["\n"], enable_langfuse=False):
        self.llm = llm
        self.engine = engine
        self.max_tries = 10
        self.prompt = None
        self.system_prompt = None
        self.bootstrap = []
        self.do_stop = False
        self.on_iteration_start = on_iteration_start
        self.on_iteration_step = on_iteration_step
        self.on_iteration_end = on_iteration_end
        self.stop_list = stop_list
        self.enable_langfuse = enable_langfuse

        self.engine.bind(self)
        self.reset()

        if self.enable_langfuse:
            self.init_langfuse()

    def init_langfuse(self):
        try:
            from langfuse.decorators import observe
        except ImportError:
            raise ImportError("Please install langfuse using pip install langfuse")
    
        self.reset = observe()(self.reset)
        self.execute_command = observe()(self.execute_command)
        self.build_initial_messages = observe()(self.build_initial_messages)
        self.clean_reply = observe()(self.clean_reply)
        self.stop = observe()(self.stop)
        self.step = observe()(self.step)
        self.run = observe()(self.run)

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
        self.history = []
        if self.system_prompt:
            self.history.append(
                dict(
                    role="system",
                    content=self.system_prompt
                ),
            )
        if self.prompt:
            self.history.append(
                dict(
                    role="user",
                    content=self.prompt
                ),
            )
        for command in self.bootstrap:
            self.execute_command(command)

    def clean_reply(self, reply):
        reply = reply.replace("\_", "_")
        reply = reply.strip()
        reply = reply[:reply.rfind(")")+1]
        return reply

    def stop(self):
        self.do_stop = True

    def step(self, transient_history=[]):
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
            
            reply = self.llm(self.history + transient_history + temp_messages, stop=self.stop_list)
            reply = self.clean_reply(reply)

            if len(reply) < 2:
                print(colored("Error: empty reply, retrying", "red"))
                temp_messages.append(dict(
                    role="assistant",
                    content="..."
                ))
                temp_messages.append(dict(
                    role="user",
                    content="Error: please provide a valid function call"
                ))
                continue

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
        
        return StepOutput(
            abort=abort,
            reply=reply,
            output=output,
            result=result,
        )

    def run(self, iterations=10, resume=False, transient_history=[]):
        if self.prompt is None and self.system_prompt is None:
            raise ValueError("You must set a prompt before running the agent")
        
        if not resume:
            if self.prompt:
                print(colored(f"prompt:\n{self.prompt}", "blue"))
            if self.system_prompt:
                print(colored(f"system_prompt:\n{self.system_prompt}", "blue"))
            self.reset()
            self.build_initial_messages()

        print(colored(f"Running {iterations if iterations > 0 else 'infinite'} iterations", "green"))
        it = 0
        while iterations < 0 or it < iterations:
            if self.on_iteration_start is not None: self.on_iteration_start(self)
            if self.do_stop:
                break

            step_output = self.step(transient_history)
            if self.on_iteration_step is not None: self.on_iteration_step(self, step_output)

            if step_output.abort:
                break

            self.history.append(dict(
                role="assistant",
                content=step_output.reply
            ))
            self.history.append(dict(
                role="user",
                content=step_output.output
            ))
            if self.on_iteration_end is not None:
                self.on_iteration_end(self)
            
            it = it + 1
        print(colored(f"Finished {iterations} iterations", "green"))
