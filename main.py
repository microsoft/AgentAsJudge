import argparse
import json
from dotenv import find_dotenv, load_dotenv
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential

from metrics.base_agentic_quality_metric import BaseAgenticQualityMetric
from metrics.agent_eval_prompts import AgentEvalPrompts
from utils import validate_env_variables, validate_jsonl

load_dotenv(find_dotenv())


def load_samples(jsonl_path):
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f]


def evaluate(samples, credential):
    print("📝 Starting evaluation of samples...\n")

    with open(r"agent_eval_prompts/introduction/reviewer_agent_system_prompt.md") as f:
        reviewer_prompt = f.read()

    with open(r"agent_eval_prompts/introduction/critic_agent_system_prompt.md") as f:
        critic_prompt = f.read()

    with open(r"agent_eval_prompts/introduction/ranker_agent_system_prompt.md") as f:
        ranker_prompt = f.read()

    with open(r"agent_eval_prompts/introduction/shared_quality_metrics.md") as f:
        shared_quality_metrics = f.read()

    agent_eval_prompts = AgentEvalPrompts(
        _shared_quality_metrics=shared_quality_metrics,
        _critic_prompt=critic_prompt,
        _reviewer_prompt=reviewer_prompt,
        _ranker_prompt=ranker_prompt
    )

    evaluation_metric = BaseAgenticQualityMetric(
        name="AgenticQualityMetric",
        agent_eval_prompts=agent_eval_prompts,
        credential=InteractiveBrowserCredential()
    )

    for idx, sample in enumerate(samples):
        print(f"🔍 Evaluating Sample {idx + 1}...")
        try:
            file_id = sample["fileMetadata"]["sourceFilePath"]
            intro = [intro_slide_generated_object["generatedContent"] for intro_slide_generated_object in
                     sample["slides"][0]["generatedObjects"] if
                     intro_slide_generated_object["status"] == "Success" and intro_slide_generated_object[
                         "type"] == "Intro"][0]
            summary = sample["fileMetadata"]["rawExtractiveSummaries"]
            result = evaluation_metric.measure(str(
                {
                    "intro": intro,
                    "summary": summary,
                }
            ))
            for r in result:
                print(f"\t\t\t📊 Score: {r.score}")
                print(f"\t\t\t🗣 Review: {r.reason}")
            print("-"* 40)
            with open("original_intros_evaluation_results.jsonl", "a", encoding="utf-8") as output_file:
                output_file.write(json.dumps({"file_id": file_id, "intro": intro, "summary": summary, "result": [json.dumps(r.__dict__) for r in result]}, ensure_ascii=False) + "\n")
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
