import re
from typing import Final

from projects.agent_llm_evaluation.agent_llm_evaluation.inner_monologue import InnerMonologue


class MonologueQualityMetric:
    """Monologue Quality Metric.
    This metric evaluates the quality of a generated item using an inner monologue agent.
    The inner monologue agent is a multi-agent system that discusses the quality of the item,
    """

    def __init__(self, inner_monologue: InnerMonologue) -> None:
        self.inner_monologue = inner_monologue
        self.name: Final[str] = "Monologue Quality Metric"

    def _get_name(self) -> str:
        return self.name

    def _evaluate(self, context: str, question:str) -> dict[str, str | list[str]]:
        generated_fitb = f"Context:\n{context}\nQuestion:\n{question}"
        final_rank = self.inner_monologue.run_task(generated_fitb).replace("TERMINATE", "")
        meta_review = re.split(r"\s*rank\s*:\s*", final_rank, maxsplit=1)
        return {
            "monologue": [str(s) for s in self.inner_monologue.get_monologue()],
            "meta_review": meta_review[0].strip(),
            "final_score": meta_review[1].strip(),
        }
