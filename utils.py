import json
import os
import sys

def validate_env_variables():
    required_vars = ["AZURE_DEPLOYMENT", "MODEL_NAME", "AZURE_ENDPOINT", "API_TOKEN"]
    missing_vars = [var for var in required_vars if os.getenv(var) is None]

    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f" - {var}")
        sys.exit(1)

    return {
        "azure_deployment": os.getenv("AZURE_DEPLOYMENT"),
        "model": os.getenv("MODEL_NAME"),
        "api_version": "2024-12-01-preview",
        "azure_endpoint": os.getenv("AZURE_ENDPOINT"),
        "api_token": os.getenv("API_TOKEN")
    }

def validate_jsonl(file_path):
    errors = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, start=1):
            try:
                obj = json.loads(line)
                if not isinstance(obj, dict):
                    errors.append(f"Line {line_num}: Not a JSON object (expected a dictionary).")
            except json.JSONDecodeError as e:
                errors.append(f"Line {line_num}: Invalid JSON. Error: {str(e)}")

    if not errors:
        print("✅ All lines are valid JSON objects!")
    else:
        print("❌ Found issues in the file:")
        for error in errors:
            print(" -", error)
