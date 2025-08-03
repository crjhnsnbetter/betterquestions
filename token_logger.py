import tiktoken
from datetime import datetime
import os

# Cost per 1K tokens (adjustable if OpenAI pricing changes)
PRICING = {
    "gpt-3.5-turbo": 0.0005,
    "gpt-4o": 0.005,
}

LOG_FILE = "token_usage_log.csv"

class TokenLogger:
    def __init__(self, model="gpt-3.5-turbo", log_file=LOG_FILE):
        self.model = model
        self.log_file = log_file
        self.total_tokens = 0
        self.total_cost = 0.0
        self.logs = []

    def count_tokens(self, text: str) -> int:
        enc = tiktoken.encoding_for_model(self.model)
        return len(enc.encode(text))

    def log(self, prompt: str, response: str, model=None, meta: dict = None):
        model = model or self.model
        input_tokens = self.count_tokens(prompt)
        output_tokens = self.count_tokens(response)
        total_tokens = input_tokens + output_tokens
        cost = (total_tokens / 1000) * PRICING.get(model, PRICING["gpt-3.5-turbo"])

        self.total_tokens += total_tokens
        self.total_cost += cost

        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",  # Safe UTC time
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "cost_usd": round(cost, 6),
        }

        if meta:
            log_entry.update(meta)

        self.logs.append(log_entry)
        self._write_log(log_entry)

    def _write_log(self, entry):
        is_new = not os.path.isfile(self.log_file)
        with open(self.log_file, "a") as f:
            if is_new:
                f.write(",".join(entry.keys()) + "\n")
            f.write(",".join(str(entry[k]) for k in entry) + "\n")

    def summary(self):
        return {
            "model": self.model,
            "total_queries": len(self.logs),
            "total_tokens": self.total_tokens,
            "estimated_cost_usd": round(self.total_cost, 6),
        }
