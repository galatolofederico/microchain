class TokenTracker:
    def __init__(self):
        self.prompt_tokens = 0
        self.completion_tokens = 0

    def update_from_usage(self, usage):
        self.prompt_tokens += usage.prompt_tokens
        self.completion_tokens += usage.completion_tokens

    def get_total_cost(self, model):
        # From https://openai.com/pricing
        if model in ["gpt-4o", "gpt-4o-2024-05-13"]:
            costs = {"prompt": 5e-6, "completion": 1.5e-05}
        elif model == "gpt-4o-2024-08-06":
            costs = {"prompt": 2.5e-06, "completion": 1e-05}
        elif model == "gpt-4-turbo":
            costs = {"prompt": 1e-05, "completion": 3e-05}
        elif model in ["gpt-4-0125-preview", "gpt-4-1106-preview", "gpt-4-turbo-preview"]:
            costs = {"prompt": 1e-05, "completion": 3e-05}
        elif model == "gpt-3.5-turbo-0125":
            costs = {"prompt": 5e-07, "completion": 1.5e-06}
        # Took from https://replicate.com/pricing
        elif model == "meta/meta-llama-3.1-405b-instruct":
            costs = {"prompt": 9.5e-06, "completion": 9.5e-06}
        # Fail gracefully
        else:
            print(f"Unsupported {model}")
            return 0

        return self.prompt_tokens * costs["prompt"] + self.completion_tokens * costs["completion"]

