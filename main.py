import requests
import json
import re
import math_tools
import sympy as sp

# ── TOOLS ─────────────────────────────────────────────────────────────────────

def add(a, b):
    return float(a) + float(b)


def subtract(a, b):
    return float(a) - float(b)


def multiply(a, b):
    return float(a) * float(b)


def divide(a, b):
    return float(a) / float(b)


TOOL_MAP = {
    # Basic arithmetic
    "add": math_tools.add,
    "subtract": math_tools.subtract,
    "multiply": math_tools.multiply,
    "divide": math_tools.divide,

    # Powers and roots
    "power": math_tools.power,
    "square_root": math_tools.square_root,
    "factorial": math_tools.factorial,
    "percentage": math_tools.percentage,
    # Algebra
    "solve_equation": math_tools.solve_equation,

    # Statistics
    "calculate_mean": math_tools.calculate_mean,
    "calculate_median": math_tools.calculate_median,
    "calculate_mode": math_tools.calculate_mode,
}

# ── CALL LLM ──────────────────────────────────────────────────────────────────
def ask_llm(prompt, max_tokens=500):
    response = requests.post(
        "http://127.0.0.1:8080/completion",
        json={
            "prompt": prompt,
            "n_predict": max_tokens,
            "temperature": 0.0
        },
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    if "content" not in data:
        raise ValueError("Local LLM returned an unexpected response.")

    return data["content"].strip()



# ── STAGE 1: PROBLEM REFINEMENT ───────────────────────────────────────────────

def refine(problem):
    refined = ask_llm(f"""Convert mathematical words into symbols and word numbers into digits.

IMPORTANT:
- Preserve every number exactly.
- Preserve all variable names exactly.
- Do not change the mathematical meaning.
- Do not solve the problem.
- Do not add or remove mathematical terms.
- Return only the rewritten problem.

Problem: {problem}
Rewritten:""")

    if len(refined) > 100:
        print("  (Using original problem as fallback)")
        refined = problem

    # Convert mathematical words into symbols
    replacements = [
        (r"\bmultiplied by\b", "*"),
        (r"\bdivided by\b", "/"),
        (r"\bplus\b", "+"),
        (r"\bminus\b", "-"),
        (r"\bequals\b", "=")
    ]

    for pattern, symbol in replacements:
        refined = re.sub(pattern, symbol, refined, flags=re.IGNORECASE)

    return refined

# ── STAGE 2: PLAN GENERATION ──────────────────────────────────────────────────

def make_plan(problem):
    prompt = f"""You are a mathematical tool selector.

Available tools:
{list(TOOL_MAP.keys())}

Convert the problem into a JSON array of steps.
Rules:
- Return ONLY one valid JSON array.
- Do not include explanations, Markdown, or additional JSON.
- Pay close attention to the order of operands in subtraction and division.
- "Subtract A from B" means calculate B - A.
- "Subtract B from A" means calculate A - B.
- For "Subtract 15 from 50", use the subtract tool with arguments [50, 15].
- For "Divide 20 by 5", use the divide tool with arguments [20, 5].
- Never reverse the order of arguments.
- For a single equation with one variable, always use "solve_equation".
- For polynomial equations, use "solve_equation" to find the roots.
- For any single equation, generate exactly ONE solve_equation step.
- Never split an equation into smaller equations or solve intermediate equations separately.
- Pass the complete original equation as one string argument.
- For percentage calculations, always use "percentage".
- The first argument must be the original number.
- The second argument must be the percentage value.
- Example: Calculate 20% of 500.
  Use percentage with arguments [500, 20].
- Use arithmetic tools only for numerical calculations.
- When a problem asks to solve an equation, use solve_equation, not simplify_expression.
- Each step must contain exactly: "step", "tool", "arguments".
- Use only tools from the available tools list.
- Never calculate or write mathematical expressions inside arguments.
- Arguments must contain only numbers, strings, or lists.
- To use a previous step's answer, use its result reference as a string.
- Use result references only when referring to the output of an earlier step.
- Never use a result reference in the first step.
- References must be written exactly as "result1", "result2", etc.
- Never repeat or recalculate a previous operation.
- Do not invent tools.
- Do not solve the problem yourself.


Example:
Problem: Find square root of 25
Output:
[{{"step": 1, "tool": "square_root", "arguments": [25]}}]

Problem: Calculate 20% of 500
Output:
[{{"step": 1, "tool": "percentage", "arguments": [500, 20]}}]

Problem: Solve 2*x + 3*x + 5 = 0
Output:
[{{"step": 1, "tool": "solve_equation", "arguments": ["2*x + 3*x + 5 = 0"]}}]

Problem: Solve x squared minus 5x plus 6 equals 0
Output:
[{{"step": 1, "tool": "solve_equation", "arguments": ["x^2 - 5*x + 6 = 0"]}}]

Problem: Find the mean of 10, 20, 30
Output:
[{{"step": 1, "tool": "calculate_mean", "arguments": [[10, 20, 30]]}}]

Problem: Find the median of 2, 4, 6, 8, 10
Output:
[{{"step": 1, "tool": "calculate_median", "arguments": [[2, 4, 6, 8, 10]]}}]

Problem: Find the mode of 2, 3, 3, 4, 5
Output:
[{{"step": 1, "tool": "calculate_mode", "arguments": [[2, 3, 3, 4, 5]]}}]

Problem: Multiply 25 by 4 and then add 50
Output:
[
    {{"step": 1, "tool": "multiply", "arguments": [25, 4]}},
    {{"step": 2, "tool": "add", "arguments": ["result1", 50]}}
]

Problem: {problem}

JSON:
"""

    raw = ask_llm(prompt)

    print("  Raw LLM response received.")

    
    decoder = json.JSONDecoder()

    for index, character in enumerate(raw):
        if character == "[":
            try:
                plan, end_index = decoder.raw_decode(raw[index:])

                # The plan must be a list of step dictionaries
                if not isinstance(plan, list) or not plan:
                    continue

                if not all(
                    isinstance(step, dict)
                    and set(step.keys()) == {"step", "tool", "arguments"}
                    for step in plan
                ):
                    continue

                # Every tool must exist in our registry
                if not all(step["tool"] in TOOL_MAP for step in plan):
                    continue

                # Correct single-equation tool selection
                if (
                    len(plan) == 1
                    and plan[0]["tool"] == "solve_linear_system"
                    and isinstance(plan[0]["arguments"], list)
                    and len(plan[0]["arguments"]) >= 1
                    and isinstance(plan[0]["arguments"][0], str)
                    and plan[0]["arguments"][0].count("=") == 1
                ):
                    plan[0]["tool"] = "solve_equation"
                    plan[0]["arguments"] = [plan[0]["arguments"][0]]

                return plan

            except (json.JSONDecodeError, TypeError):
                continue

    raise ValueError("No valid mathematical tool plan was found.")




# ── STAGE 3: PLAN EXECUTION ───────────────────────────────────────────────────


def execute(plan):
    results = {}

    for step in plan:
        n = step["step"]
        tool_name = step["tool"]

        if tool_name not in TOOL_MAP:
            raise ValueError(f"Unknown mathematical tool: {tool_name}")

        tool = TOOL_MAP[tool_name]

        # Get arguments supplied by the LLM
        arguments = step["arguments"]

        # Replace references to previous results
        resolved_arguments = []

        for value in arguments:
            if isinstance(value, str) and value in results:
                # Reference to a previous step
                resolved_arguments.append(results[value])

            elif isinstance(value, str) and re.fullmatch(r"[+-]?\d+", value):
                # Convert integer strings like "144" into 144
                resolved_arguments.append(int(value))

            elif isinstance(value, str) and re.fullmatch(
                r"[+-]?(?:\d+\.\d*|\.\d+)(?:[eE][+-]?\d+)?", value
            ):
                # Convert decimal strings like "12.5" into numbers
                resolved_arguments.append(float(value))

            else:
                resolved_arguments.append(value)

        # Execute the selected mathematical function
        result = tool(*resolved_arguments)

        results[f"result{n}"] = result

        print(f"  Step {n}: {tool_name}{tuple(resolved_arguments)} = {result}")

    return result, results



# ── STAGE 4: VERIFICATION ─────────────────────────────────────────────────────

def verify(problem, answer, intermediate_results):
    print("  Asking Qwen to solve independently...")
    print("  Sending verification prompt to Qwen...")

    recheck = ask_llm(
        prompt=f"""Solve this mathematical problem independently.

You must calculate every operation in the exact order given.

For each operation:
1. Identify the operation and its operands.
2. Calculate the result.
3. Use that result in the next operation.   
Important rules:
- Include exactly ONE value in "steps" for each operation.
- Never repeat a result.
- Do not include the final answer again in "steps" unless it is the result of the final operation.
- For a single-step problem, "steps" must contain exactly one value.

Check your arithmetic before responding.
For median calculations:
- Extract ALL numbers from the original problem.
- Sort the numbers in ascending order.
- If the count is odd, return the middle number.
- If the count is even, calculate the average of
  the two middle numbers.
- Include ALL original input numbers in "steps".
- The "answer" must be a numerical value, never a string.
- Never return empty steps.

Example:
Problem: Find the median of 5, 12, 8, 20, 15
Output:
{{"steps": [5, 12, 8, 20, 15], "answer": 12}}

Example:
Problem: Find the median of 10, 20, 30, 40
Output:
{{"steps": [10, 20, 30, 40], "answer": 25}}
  For equation-solving problems:
- You must solve the equation completely.
- For linear equations, return the variable value.
- For quadratic equations, return BOTH roots.
- Never return the original equation as the answer.
- The answer must contain only numerical value(s).
- For multiple roots, return a JSON array of numbers.
- Include the roots in "steps" as well.
- For polynomial equations of degree 2 or higher,
  find ALL real roots.
- Never return only the first root.
- If there are multiple roots, answer must be a JSON array.
- The number of values in "answer" must include every root.
- Check that substituting each root into the original
  equation gives zero.

Example:
Problem: Solve 2*x + 3 = 7
Output:
{{"steps": [2], "answer": 2}}

Example:
Problem: Solve 2*x^2 - 7*x + 3 = 0
Output:
{{"steps": [0.5, 3], "answer": [0.5, 3]}}

Return ONLY one valid JSON object.
Do not include explanations outside the JSON.
For algebraic expressions containing variables:
- Preserve all variables exactly.
- Combine like terms correctly.
- Do not replace variables with numbers.
- Return the complete simplified expression as a string.
- Do not return individual coefficients as the final answer.
- Example:
  Problem: Simplify 2x + 3x + 5
  Output:
  {{"steps": ["5*x + 5"], "answer": "5*x + 5"}}

The JSON format must be:
{{
    "steps": [20, 5],
    "answer": 5
}}

For a single-step problem, include one value in "steps".

Problem: {problem}

JSON:""",
        max_tokens=100
    )

    print("  Verification prompt sent.")
    print("  Qwen's independent response:", recheck)
    print("  Original problem sent to Qwen:", problem)

    # Extract the first JSON object from Qwen's response
    try:
        decoder = json.JSONDecoder()
        start = recheck.find("{")

        if start == -1:
            raise ValueError("No JSON answer found.")

        qwen_data, end = decoder.raw_decode(recheck[start:])

        if not isinstance(qwen_data, dict):
            raise ValueError("Response must be a JSON object.")

        if "answer" not in qwen_data or "steps" not in qwen_data:
            raise ValueError("Missing answer or steps.")

        qwen_answer = qwen_data["answer"]
        qwen_steps = qwen_data["steps"]

        if not isinstance(qwen_steps, list):
            raise ValueError("Steps must be a list.")
        if qwen_answer is None or isinstance(qwen_answer, bool):
            raise ValueError("Invalid final answer.")
        if any(isinstance(step, bool) or step is None for step in qwen_steps):
            raise ValueError("Invalid intermediate step.")

    except (json.JSONDecodeError, ValueError, KeyError, TypeError):
        print("  Verdict: Could not verify.")
        return

    try:
        # Case 1: Symbolic expressions
        if isinstance(answer, sp.Expr) and not answer.is_number:

            if isinstance(qwen_answer, list) and len(qwen_answer) == 1:
                qwen_answer = qwen_answer[0]

            if not isinstance(qwen_answer, str):
                print("  Verdict: Could not verify symbolic expression.")
                return

            qwen_expression = math_tools.safe_sympify(qwen_answer)

            difference = sp.simplify(answer - qwen_expression)

            if difference == 0:
                print("  Verdict: AGREEMENT ✓")
            else:
                print("  Verdict: DISAGREEMENT ✗")
                print("  Python result:", answer)
                print("  Qwen result:", qwen_expression)

        # Case 2: Numeric answers or lists of answers
        else:
            python_steps = list(intermediate_results.values())

            print("  Python intermediate results:", python_steps)
            print("  Qwen intermediate results:", qwen_steps)
            if len(python_steps) != len(qwen_steps):
                print("  Intermediate Step Verification: DIFFERENT NUMBER OF STEPS")
            else:

                steps_match = True

                for python_step, qwen_step in zip(python_steps, qwen_steps):
                    if abs(float(python_step) - float(qwen_step)) >= 0.001:
                        steps_match = False
                        break

                if steps_match:
                    print("  Intermediate Step Verification: AGREEMENT ✓")
                else:
                    print("  Intermediate Step Verification: DISAGREEMENT ✗")

            if isinstance(qwen_answer, list):
                qwen_values = [float(value) for value in qwen_answer]
            else:
                qwen_values = [float(qwen_answer)]

            if isinstance(answer, (list, tuple)):
                python_values = [float(value) for value in answer]
            else:
                python_values = [float(answer)]

            print("  Python result:", python_values)
            print("  Qwen result:", qwen_values)

            unmatched = qwen_values.copy()

            for value in python_values:
                match = next(
                    (
                        other for other in unmatched
                        if abs(value - other) < 0.001
                    ),
                    None
                )

                if match is None:
                    print("  Verdict: DISAGREEMENT ✗")
                    return

                unmatched.remove(match)

            if not unmatched:
                print("  Verdict: AGREEMENT ✓")
            else:
                print("  Verdict: DISAGREEMENT ✗")

    except (ValueError, TypeError, SyntaxError) as error:
        print("  Verdict: Could not verify.")
        print("  Reason:", error)

# ── MAIN ──────────────────────────────────────────────────────────────────────

def run():
    while True:
        problem = input("\nEnter problem (or exit): ")

        if problem == "exit":
            break

        print("\n[Stage 1] Refining problem...")
        refined = refine(problem)
        print(f"  {refined}")

        print("\n[Stage 2] Generating plan...")

        try:
            plan = make_plan(refined)
            print(f"  {plan}")

        except Exception as e:
            print("  Could not generate plan.")
            print("  Error:", repr(e))
            continue

        print("\n[Stage 3] Executing plan...")

        try:
            answer, intermediate_results = execute(plan)
            print(f"  Final Answer: {answer}")

        except Exception as e:
            print(f"  Execution failed: {e}")
            continue

        print("\n[Stage 4] Verifying answer...")
        verify(problem, answer, intermediate_results)
    


if __name__ == "__main__":
    run()