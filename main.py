import requests
import json
import re


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
    "add": add,
    "subtract": subtract,
    "multiply": multiply,
    "divide": divide,
}


# ── CALL LLM ──────────────────────────────────────────────────────────────────

def ask_llm(prompt):
    response = requests.post(
        "http://localhost:8080/completion",
        json={
            "prompt": prompt,
            "n_predict": 200,
            "temperature": 0.0
        }
    )
    return response.json()["content"].strip()


# ── STAGE 1: PROBLEM REFINEMENT ───────────────────────────────────────────────

def refine(problem):
    refined = ask_llm(f"""Convert any word numbers to digits. Keep it very short.
Do NOT solve. Do NOT explain. Only rewrite with digits.
Example: "multiply twenty and three and add five" → "multiply 20 and 3 and add 5"
Problem: {problem}
Rewritten:""")

    if len(refined) > 100:
        print("  (Using original problem as fallback)")
        return problem

    return refined


# ── STAGE 2: PLAN GENERATION ──────────────────────────────────────────────────

def make_plan(problem):
    prompt = f"""Break this math problem into steps.
Problem: {problem}
Use only these tools: add, subtract, multiply, divide.
Reply ONLY with JSON. No text before or after.
Use "result1", "result2" to pass previous answers.
JSON:
[{{"step":1,"tool":"multiply","a":"30","b":"2"}},
 {{"step":2,"tool":"divide","a":"result1","b":"4"}}]
Now solve:
"""

    raw = "[" + ask_llm(prompt)
    start = raw.index("[")
    end = raw.rindex("]") + 1

    return json.loads(raw[start:end])


# ── STAGE 3: PLAN EXECUTION ───────────────────────────────────────────────────

def execute(plan):
    results = {}

    for step in plan:
        n = step["step"]

        a = results.get(step["a"], step["a"])
        b = results.get(step["b"], step["b"])

        result = TOOL_MAP[step["tool"]](a, b)

        results[f"result{n}"] = result

        print(
            f"  Step {n}: {step['tool']}({a}, {b}) = {result}"
        )

    return result


# ── STAGE 4: VERIFICATION ─────────────────────────────────────────────────────

def verify(problem, answer):
    recheck = ask_llm(
        f"Solve this and give only the number answer: "
        f"{problem}\nAnswer:"
    )

    # Extract the first number from the response
    match = re.search(r'-?\d+(\.\d+)?', recheck.strip())

    if match:
        recheck_value = float(match.group())

        if abs(recheck_value - float(answer)) < 0.001:
            print("  Verdict: CORRECT ✓")
        else:
            print(
                f"  Verdict: WRONG ✗ "
                f"(expected {recheck_value}, got {answer})"
            )
    else:
        print(
            f"  Verdict: Could not verify. LLM said: {recheck}"
        )


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

        except Exception:
            print("  Could not generate plan. Try again!")
            continue

        print("\n[Stage 3] Executing plan...")

        try:
            answer = execute(plan)
            print(f"  Final Answer: {answer}")

        except Exception as e:
            print(f"  Execution failed: {e}")
            continue

        print("\n[Stage 4] Verifying answer...")
        verify(refined, answer)


run()