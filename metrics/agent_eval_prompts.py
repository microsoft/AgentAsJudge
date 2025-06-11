from dataclasses import dataclass


@dataclass(frozen=True)
class AgentEvalPrompts:
    """
    Class to hold the prompts for agent evaluation.
    """
    critic_prompt: str
    reviewer_prompt: str
    ranker_prompt: str