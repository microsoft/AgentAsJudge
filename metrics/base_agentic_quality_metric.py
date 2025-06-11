import ast
import os
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from azure.core.credentials import TokenCredential

from agent_llm_evaluation.agent_llm_evaluation.inner_monologue import InnerMonologue
from metrics.agent_eval_prompts import AgentEvalPrompts

@dataclass(frozen=True)
class Measurement:
    """
    Represents measured values of a metric for a test case.
    """

    score: float
    reason: str
    is_successful: Optional[bool]

    @staticmethod
    def undetermined(reason: str) -> "Measurement":
        """
        Create an undetermined measurement.
        """
        return Measurement(score=float("nan"), reason=reason, is_successful=None)

class QualityLevel(Enum):
    """
    Quality level of the content on a scale of 1 to 5 - higher is better.
    """

    Bad = 1
    Poor = 2
    Fair = 3
    Good = 4
    Excellent = 5

class BaseAgenticQualityMetric:
    """
    Base class for agentic quality metrics.
    """

    def _get_name(self) -> str:
        return self.name

    def __init__(self, name: str, agent_eval_prompts: AgentEvalPrompts, credential:TokenCredential) -> None:
        self.name = name
        self.agent_eval_prompts = agent_eval_prompts
        self.inner_monologue = InnerMonologue(
            api_token=os.getenv("API_TOKEN"),
            agent_eval_prompts=self.agent_eval_prompts,
            azure_deployment=os.getenv("AZURE_DEPLOYMENT"),
            model_name=os.getenv("MODEL_NAME"),
            azure_endpoint=os.getenv("AZURE_ENDPOINT"),
        )

    def _measure(self, scenario: str) -> list[Measurement]:
        metric_response = self.inner_monologue.run_task(scenario)

        if metric_response is None:
            return [Measurement.undetermined(reason="Failed: Unable to generate a ranking")]

        meta_review = metric_response.replace("TERMINATE","").strip()

        ranker_json = ast.literal_eval(meta_review)

        evaluation = [Measurement(
            score=measurement["score"],
            reason=measurement["reason"],
            is_successful=True,
        ) for measurement in ranker_json.values()]

        return evaluation

    def measure(self, scenario: str) -> list[Measurement]:
        """
        Measures the performance of a model.
        @param scenario: scenario to be measured.
        @return: the evaluation result.
        """
        return self._measure(scenario)
