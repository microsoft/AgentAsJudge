import ast
from dataclasses import dataclass
from pathlib import Path


@dataclass
class InputSample:
    context: str
    question: str
    uid: int


@dataclass
class Dataset:
    samples: list[InputSample]
    output_file: Path
    lock_path: Path = ""  # filled after creation

    def __init__(self, jsonl_path: Path, output_file: Path):
        self.samples = self._load_samples(jsonl_path)
        self.output_file = output_file
        self.lock_path = Path(f"{output_file}.lock")
        self.lock_path.touch(exist_ok=True)

    @staticmethod
    def _load_samples(jsonl_path: Path) -> list[InputSample]:
        """Load all non-blank lines in the JSONL file into a list of dicts."""
        with open(jsonl_path, encoding="utf-8") as f:
            chunks = [ast.literal_eval(c.strip()) for c in f.readlines()]
        return [
            InputSample(
                context=chunk["context"],
                question=chunk["question"],
                uid=i,
            )
            for i, chunk in enumerate(chunks)
        ]
