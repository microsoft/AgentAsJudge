# README

## Project Overview
This project evaluates the agentic quality of text samples using a multi-agent reasoning pipeline. It leverages Azure OpenAI services and a set of predefined prompts to assess the quality of content on a scale of 1 to 5, providing constructive feedback and scoring.

### Features Offered
- **Multi-Agent Evaluation**: Includes discussion, criticism, and ranking agents to evaluate text samples.
- **Customizable Prompts**: Prompts for agents can be tailored to specific evaluation needs.
- **Scoring and Feedback**: Provides a score (1–10) and detailed feedback for each sample.
- **Azure Integration**: Utilizes Azure OpenAI services for model inference.

---

## Prerequisites
1. **Python**: Ensure Python 3.8+ is installed.
2. **Dependencies**: Install required Python packages using:
   ```bash
   pip install -r requirements.txt
   ```
3. **Azure Credentials**: Set up Azure credentials and environment variables:
   - `AZURE_DEPLOYMENT`
   - `MODEL_NAME`
   - `AZURE_ENDPOINT`
   - `API_TOKEN`
4. **Input File**: Prepare a `.jsonl` file containing JSON objects (one per line) that includes all the information needed by the evaluation model.

---

## How to Run
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/microsoft-mousa/agentAsAJudge
   cd agentAsAJudge
   ```

2. **Set Up Environment Variables**:
   Create a `.env` file in the project root and add the following:
   ```env
   AZURE_DEPLOYMENT=<your-deployment-name>
   MODEL_NAME=<your-model-name>
   AZURE_ENDPOINT=<your-endpoint-url>
   API_TOKEN=<your-api-token>
   ```

3. **Change System Prompts**:
   To customize the system prompts:
   - Create a new directory under `metrics` and add your prompt files (e.g., `.md` files).
   - Update the initialization of the `AgentEvalPrompts` object in `main.py` with the paths to your new prompt files:
     ```python
     agent_eval_prompts = AgentEvalPrompts(
         reviewer_prompt="<path-to-your-reviewer-prompt>",
         critic_prompt="<path-to-your-critic-prompt>",
         ranker_prompt="<path-to-your-ranker-prompt>"
     )
     ```

4. **Run Evaluation**:
   Execute the script:
   ```bash
   python main.py <path-to-jsonl-file>
   ```

---

## Expected Output
1. **Validation**:
   - If the `.jsonl` file is valid:
     ```
     ✅ All lines are valid JSON objects!
     ```
   - If there are issues:
     ```
     ❌ Found issues in the file:
      - Line X: <error-description>
     ```

2. **Evaluation**:
   For each sample, the output includes:
   - **Score**: A numeric value (1–10).
   - **Feedback**: Detailed reasoning for the score.

   Example:
   ```
   🔍 Evaluating Sample 1...
   📊 Score: 4
   🗣 Review: The content is well-structured and informative.
   ```

3. **Errors**:
   If evaluation fails for a sample:
   ```
   ❌ Error evaluating sample X: <error-description>
   ```

---

## Contribution
Feel free to contribute by improving prompts, adding new metrics, or enhancing the evaluation pipeline.
