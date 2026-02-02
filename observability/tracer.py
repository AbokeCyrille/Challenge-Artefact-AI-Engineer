# observability/tracer.py
import time
import uuid

class TraceRun:
    def __init__(self, question: str):
        self.run_id = str(uuid.uuid4())
        self.question = question
        self.start_time = time.time()
        self.events = []
        self.tokens = 0

    def log(self, step: str, data: dict = None):
        self.events.append({
            "step": step,
            "timestamp": time.time(),
            "data": data or {}
        })

    def set_tokens(self, n_tokens: int):
        self.tokens = n_tokens

    def finish(self, answer: str):
        self.end_time = time.time()
        self.latency = self.end_time - self.start_time
        self.answer = answer

    def to_dict(self):
        return {
            "run_id": self.run_id,
            "question": self.question,
            "latency": round(self.latency, 3),
            "tokens": self.tokens,
            "events": self.events
        }
