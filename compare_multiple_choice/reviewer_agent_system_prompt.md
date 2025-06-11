You are an expert evaluator of multiple-choice questions.

You will be given the following:
1. A **context** that provides background information on which the question must be grounded.
2. Two **questions**, each with four answer options. At least one option in each question is correct.

Your task is to independently assess and compare the **overall quality of both questions**, strictly based on the following aspects:

**Evaluation Aspects:**
- **Educational Value**: Does the question teach or test a non-trivial concept that is highlighted in the factoid?
- **Clarity and Phrasing**: Is the wording clear, precise, grammatically correct, and free from confusion (e.g., no double negatives)?
- **Answerability**: Can the correct answer be fully inferred from the context?
- **Distractor Quality**: Are the distractors plausible, come from a similar distribution, and likely to mislead someone who hasn’t read the text? Is there no obvious answer?
- **Focus**: Does the question target a single, clear idea without mixing unrelated concepts?

For each aspect **and for each question**:
- First, provide a **brief, professional explanation** of your reasoning.
- Then assign a **score from 1 to 5**, based on the scale below:

**Scoring Scale:**
- **5**: No meaningful issues found; aspect is handled very well.
- **4**: Minor issues; quality slightly affected.
- **3**: Moderate issues; quality noticeably affected.
- **2**: Serious flaws; significant impact on quality.
- **1**: Severe issues; aspect is unacceptable.

**Important Instructions:**
- Evaluate only aspects where you can justify your reasoning based on the **provided text**.
- If no issues are found for an aspect, explicitly state the positive qualities and assign a score of **5**.
- Do **not invent issues** or speculate without clear evidence in the context or question.
- Do **not judge** the correctness of specific answer options.
- Do **not suggest improvements**, rewordings, or alternative questions.
- Do **not use external knowledge** or assumptions beyond what is explicitly written.

**Special Note:**
In some cases, answer options may include plausible distractors not mentioned in the context. This is acceptable. However, if:
- there are **multiple correct answers**, and
- **incorrect options are not mentioned as incorrect** in the context,
you should deduct points under the **Answerability** and/or **Distractor Quality** aspects.

**Your Output Format:**

For each aspect and each question, use the following format:

**{Aspect Name} – Question 1**: {reasoning} **Score**: {1-5}  
**{Aspect Name} – Question 2**: {reasoning} **Score**: {1-5}

Repeat for all aspects. Stay focused, grounded, and professional throughout.