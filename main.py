import argparse
import json
from dotenv import find_dotenv, load_dotenv
from azure.identity import DefaultAzureCredential

from metrics.base_agentic_quality_metric import BaseAgenticQualityMetric
from metrics.agent_eval_prompts import AgentEvalPrompts
from utils import validate_env_variables, validate_jsonl

load_dotenv(find_dotenv())


def load_samples(jsonl_path):
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f]


def evaluate(samples, credential):
    print("📝 Starting evaluation of samples...\n")

    with open(r"agent_eval_prompts/multiple_choice/reviewer_agent_system_prompt.md") as f:
        reviewer_prompt = f.read()

    with open(r"agent_eval_prompts/multiple_choice/critic_agent_system_prompt.md") as f:
        critic_prompt = f.read()

    with open(r"agent_eval_prompts/multiple_choice/ranker_agent_system_prompt.md") as f:
        ranker_prompt = f.read()

    agent_eval_prompts = AgentEvalPrompts(
        reviewer_prompt=reviewer_prompt,
        critic_prompt=critic_prompt,
        ranker_prompt=ranker_prompt
    )

    evaluation_metric = BaseAgenticQualityMetric(
        name="AgenticQualityMetric",
        agent_eval_prompts=agent_eval_prompts,
        credential=credential
    )

    for idx, sample in enumerate(samples):
        print(f"🔍 Evaluating Sample {idx + 1}...")
        try:
            result = evaluation_metric.measure(str(sample))
            for r in result:
                print(f"📊 Score: {r.score}")
                print(f"🗣 Review: {r.reason}")
        except Exception as e:
            print(f"❌ Error evaluating sample {idx + 1}: {e}\n")

def main():
    parser = argparse.ArgumentParser(description="Validate JSONL structure and Azure env variables, then evaluate.")
    parser.add_argument("jsonl_path", help="Path to the JSONL file.")
    args = parser.parse_args()

    print("🔍 Validating Azure environment variables...")
    azure_config = validate_env_variables()

    print("📄 Validating JSONL structure...")
    validate_jsonl(args.jsonl_path)

    print("\n✅ Environment is ready for Azure deployment!")
    print(f"Using deployment: {azure_config['azure_deployment']}")
    print(f"Model name: {azure_config['model']}")
    print(f"Endpoint: {azure_config['azure_endpoint']}")

    samples = load_samples(args.jsonl_path)
    evaluate(samples, DefaultAzureCredential())


if __name__ == "__main__":
    main()
