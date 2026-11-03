# Mathematical Calculation Agent – Improved

An AI-powered mathematical calculation agent that converts natural-language math problems into structured tool-execution plans, performs calculations using Python, and independently verifies results using a local Large Language Model (LLM).

## Overview

This project combines the natural-language understanding capabilities of an LLM with reliable Python-based mathematical computation.

Instead of depending entirely on an LLM to calculate answers, the agent interprets the problem, generates a structured execution plan, selects appropriate mathematical tools, executes calculations using Python and SymPy, and independently verifies the result using the LLM.

**Core Principle:** The LLM understands and plans, while Python performs the calculations.

## Features

The agent provides 12 mathematical tools:

### 1. Arithmetic

- Addition
- Subtraction
- Multiplication
- Division

### 2. Powers and Roots

- Power calculation
- Square root
- Factorial

### 3. Algebra

- Linear equation solving
- Quadratic equation solving

### 4. Other Calculations

- Percentage calculation
- Mean
- Median
- Mode

## Architecture and Workflow

1. **User Input:** Accepts mathematical problems in natural language.
2. **Problem Refinement:** Uses Qwen2.5 to refine the input.
3. **Plan Generation:** Generates a structured JSON plan containing the required tools and arguments.
4. **Tool Execution:** Executes the selected mathematical operations using Python and SymPy.
5. **Independent Verification:** Asks the LLM to solve the original problem independently.
6. **Result Comparison:** Compares the Python-generated result with the LLM-generated answer.

## Technology Stack

- Python
- Qwen2.5 1.5B Instruct
- llama.cpp
- SymPy
- Requests

## Project Structure

```text
Mathematical-Calculation-Agent-Improved/
│
├── main.py
├── math_tools.py
├── .gitignore
└── README.md

```bash
pip install -r requirements.txt
