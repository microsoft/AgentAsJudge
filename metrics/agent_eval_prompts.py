from dataclasses import dataclass


@dataclass(frozen=True)
class AgentEvalPrompts:
    """
    Class to hold the prompts for agent evaluation.
    """
    _shared_quality_metrics: str
    _critic_prompt: str
    _reviewer_prompt: str
    _ranker_prompt: str

    def get_critic_prompt(self) -> str:
        """
        Returns the critic prompt.
        """
        return self._critic_prompt.format(shared_quality_metrics=self._shared_quality_metrics)

    def get_reviewer_prompt(self) -> str:
        """
        Returns the reviewer prompt.
        """
        return self._reviewer_prompt.format(shared_quality_metrics=self._shared_quality_metrics)

    def get_ranker_prompt(self) -> str:
        """
        Returns the ranker prompt.
        """
        return self._ranker_prompt.format(shared_quality_metrics=self._shared_quality_metrics)