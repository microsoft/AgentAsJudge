import argparse
import json
from pathlib import Path

from dotenv import find_dotenv, load_dotenv
from azure.identity import InteractiveBrowserCredential

from metrics.base_agentic_quality_metric import BaseAgenticQualityMetric
from metrics.agent_eval_prompts import AgentEvalPrompts
from utils import validate_env_variables, validate_jsonl

load_dotenv(find_dotenv())

SUPPORTED_TASK_TYPES = ("introduction", "summary")
DEFAULT_OUTPUT_FILES = {
    "introduction": "introduction_evaluation_results.jsonl",
    "summary": "summary_evaluation_results.jsonl",
}


def load_samples(jsonl_path):
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]


def load_agent_eval_prompts(task_type: str) -> AgentEvalPrompts:
    """Load all prompt templates for the given task type."""
    prompt_dir = Path("agent_eval_prompts") / task_type

    try:
        with open(prompt_dir / "reviewer_agent_system_prompt.md", encoding="utf-8") as f:
            reviewer_prompt = f.read()

        with open(prompt_dir / "critic_agent_system_prompt.md", encoding="utf-8") as f:
            critic_prompt = f.read()

        with open(prompt_dir / "ranker_agent_system_prompt.md", encoding="utf-8") as f:
            ranker_prompt = f.read()

        with open(prompt_dir / "shared_quality_metrics.md", encoding="utf-8") as f:
            shared_quality_metrics = f.read()
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Missing prompt file for task type '{task_type}' in '{prompt_dir}'."
        ) from exc

    return AgentEvalPrompts(
        _shared_quality_metrics=shared_quality_metrics,
        _critic_prompt=critic_prompt,
        _reviewer_prompt=reviewer_prompt,
        _ranker_prompt=ranker_prompt,
    )


def build_introduction_scenario(sample: dict, sample_index: int) -> tuple[str, dict]:
    """Build the evaluation scenario string and output record for introduction samples."""
    try:
        file_metadata = sample["fileMetadata"]
        generated_objects = sample["slides"][0]["generatedObjects"]
        intro = next(
            obj["generatedContent"]
            for obj in generated_objects
            if obj.get("status") == "Success" and obj.get("type") == "Intro"
        )
        summary = file_metadata["rawExtractiveSummaries"]
        file_id = file_metadata.get("sourceFilePath", f"sample_{sample_index}")
    except (KeyError, IndexError, StopIteration) as exc:
        raise ValueError(
            "Invalid introduction sample schema. Expected keys: "
            "fileMetadata.sourceFilePath, fileMetadata.rawExtractiveSummaries, "
            "slides[0].generatedObjects with a successful Intro object."
        ) from exc

    payload = {"intro": intro, "summary": summary}
    output_record = {"file_id": file_id, **payload}
    return json.dumps(payload, ensure_ascii=False), output_record


def build_summary_scenario(sample: dict, sample_index: int) -> tuple[str, dict]:
    """Build the evaluation scenario string and output record for summary samples."""
    source_material = sample.get("source_material") or sample.get("source") or sample.get("context")
    summary = sample.get("summary") or sample.get("generated_summary")

    if source_material is None or summary is None:
        raise ValueError(
            "Invalid summary sample schema. Expected keys: "
            "source_material (or source/context) and summary (or generated_summary)."
        )

    sample_id = sample.get("file_id") or sample.get("id") or f"sample_{sample_index}"
    payload = {"source_material": source_material, "summary": summary}
    output_record = {"sample_id": sample_id, **payload}
    return json.dumps(payload, ensure_ascii=False), output_record


SCENARIO_BUILDERS = {
    "introduction": build_introduction_scenario,
    "summary": build_summary_scenario,
}


def evaluate(samples, credential, task_type: str, output_file: str):
    print(f"📝 Starting evaluation of samples for task type: {task_type}\n")

    agent_eval_prompts = load_agent_eval_prompts(task_type)
    build_scenario = SCENARIO_BUILDERS[task_type]

    evaluation_metric = BaseAgenticQualityMetric(
        name="AgenticQualityMetric",
        agent_eval_prompts=agent_eval_prompts,
        credential=credential,
    )

    for idx, sample in enumerate(samples):
        print(f"🔍 Evaluating Sample {idx + 1}...")
        try:
            scenario, output_record = build_scenario(sample=sample, sample_index=idx + 1)
            result = evaluation_metric.measure(scenario)

            for r in result:
                print(f"\t\t\t📊 Score: {r.score}")
                print(f"\t\t\t🗣 Review: {r.reason}")
            print("-" * 40)

            with open(output_file, "a", encoding="utf-8") as f:
                f.write(
                    json.dumps(
                        {**output_record, "result": [m.__dict__ for m in result]},
                        ensure_ascii=False,
                    )
                    + "\n"
                )
        except Exception as e:
            print(f"❌ Error evaluating sample {idx + 1}: {e}\n")


def main():
    parser = argparse.ArgumentParser(description="Validate JSONL structure and Azure env variables, then evaluate.")
    parser.add_argument("jsonl_path", help="Path to the JSONL file.")
    parser.add_argument(
        "--task-type",
        default="introduction",
        choices=SUPPORTED_TASK_TYPES,
        help="Evaluation task type. Determines which prompts and input schema to use.",
    )
    parser.add_argument(
        "--output-file",
        default=None,
        help="Output JSONL file path. Defaults based on task type.",
    )
    args = parser.parse_args()

    print("🔍 Validating Azure environment variables...")
    azure_config = validate_env_variables()

    print("📄 Validating JSONL structure...")
    validate_jsonl(args.jsonl_path)

    print("\n✅ Environment is ready for Azure deployment!")
    print(f"Using deployment: {azure_config['azure_deployment']}")
    print(f"Model name: {azure_config['model']}")
    print(f"Endpoint: {azure_config['azure_endpoint']}")
    print(f"Task type: {args.task_type}")

    output_file = args.output_file or DEFAULT_OUTPUT_FILES[args.task_type]
    print(f"Output file: {output_file}")

    samples = load_samples(args.jsonl_path)
    evaluate(
        samples=samples,
        credential=InteractiveBrowserCredential(),
        task_type=args.task_type,
        output_file=output_file,
    )


if __name__ == "__main__":
    main()
