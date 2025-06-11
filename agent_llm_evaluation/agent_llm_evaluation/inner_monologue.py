import asyncio
from pathlib import Path

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import TaskResult
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from azure.core.credentials import TokenCredential
from azure.identity.aio import DefaultAzureCredential, get_bearer_token_provider

from metrics.agent_eval_prompts import AgentEvalPrompts


class InnerMonologue:
    """Synchronous multi-agent reasoning with RAG criticism.

    Agents:
      - DiscussionAgent: Discusses core quality aspects.
      - CriticAgent: RAG agent that provides constructive feedback.
      - RankerAgent: Assigns a score 1–5 based on discussion & criticism.
      - EnderAgent: Ends the discussion once feedback is sufficient.

    Memory:
      - overall_feedbacks: list of user feedback entries.
    """

    def __init__(self, azure_deployment: str, model_name:str, azure_endpoint:str, credential:DefaultAzureCredential,
                 agent_eval_prompts: AgentEvalPrompts) -> None:
        self.model_client = AzureOpenAIChatCompletionClient(
            azure_deployment=azure_deployment,
            model=model_name,
            api_version="2024-12-01-preview",
            azure_endpoint=azure_endpoint,
            temperature=0.5,
            azure_ad_token_provider=get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default"),
        )
        self.messages: list[TextMessage | TaskResult] = []
        self.overall_feedbacks: list[dict[str, str | int]] = []
        self.termination_token = "TERMINATE"

        # Prompts
        reviewer_agent_system_prompt = agent_eval_prompts.get_reviewer_prompt()

        critic_agent_system_prompt = agent_eval_prompts.get_critic_prompt()

        ranker_agent_system_prompt = agent_eval_prompts.get_ranker_prompt()

        # Discussion agent
        self.discussion_agent = AssistantAgent(
            name="DiscussionAgent",
            model_client=self.model_client,
            system_message=reviewer_agent_system_prompt,
        )

        # Critic agent
        self.critic_agent = AssistantAgent(
            name="CriticAgent",
            model_client=self.model_client,
            system_message=critic_agent_system_prompt,
        )

        # Ranker agent
        self.ranker_agent = AssistantAgent(
            name="RankerAgent", model_client=self.model_client, system_message=ranker_agent_system_prompt
        )

        # Termination when 'END_DISCUSSION' is mentioned
        self.termination = TextMentionTermination(self.termination_token)

        # Build the RoundRobin group chat
        self.team = RoundRobinGroupChat(
            participants=[
                self.discussion_agent,
                self.critic_agent,
                self.ranker_agent,
            ],
            termination_condition=self.termination,
        )

    def run_task(self, sample_text: str) -> str | None:
        """Run the multi-agent pipeline synchronously and return the final rank."""
        # Clear previous state
        self.messages.clear()

        # Recreate the RoundRobinGroupChat to avoid residual state
        self.team = RoundRobinGroupChat(
            participants=[
                self.discussion_agent,
                self.critic_agent,
                self.ranker_agent,
            ],
            termination_condition=self.termination,
        )

        # Run the conversation and collect all messages
        result = asyncio.run(self.team.run(task=sample_text))
        history = result.messages

        final_rank: str | None = None
        for msg in history:
            self.messages.append(msg)
            if isinstance(msg, TextMessage) and msg.source == self.ranker_agent.name:
                final_rank = msg.content.strip()

        return final_rank

    def get_monologue(self) -> list[dict]:
        """Return the full sequence of messages and events from the last run."""
        return [{msg.source: msg.content} for msg in self.messages if msg.source != "user"]
