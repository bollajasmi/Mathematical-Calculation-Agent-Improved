# Mathematical Calculation Agent using Local LLM

A local LLM-based mathematical calculation agent developed as part of an
internship project at Bhabha Atomic Research Centre (BARC), Visakhapatnam.

The project combines a locally deployed language model with Python-based
mathematical tools to process mathematical problems written in natural
language.

## Project Overview

The agent processes a mathematical problem through four stages:

1. Problem Refinement
2. Plan Generation
3. Plan Execution
4. Result Verification

The system uses a locally deployed Qwen2.5-1.5B-Instruct model through
llama.cpp.

## How It Works

### 1. Problem Refinement

The local LLM converts number words into digits without solving the problem.

Example:

Input:
multiply twenty and three and add five

Refined:
multiply 20 and 3 and add 5

### 2. Plan Generation

The LLM generates a structured JSON plan using four available tools:

- add
- subtract
- multiply
- divide

Previous results can be passed between steps using references such as
`result1` and `result2`.

### 3. Plan Execution

The generated plan is executed using Python functions.

The actual arithmetic operations are performed by Python rather than by the
LLM.

### 4. Result Verification

The LLM independently solves the problem again.

The result from the LLM is compared with the result produced by the Python
tools. If the results match within a small tolerance, the answer is marked
as correct.

## Architecture

User Input
    |
    v
Problem Refinement
    |
    v
Local Qwen2.5 LLM
    |
    v
JSON Calculation Plan
    |
    v
Python Mathematical Tools
    |
    v
Final Result
    |
    v
LLM Verification

## Technologies Used

- Python
- Qwen2.5-1.5B-Instruct
- llama.cpp
- Requests
- JSON
- Regular Expressions
- Local LLM inference

## Model

Model used during development:

`Qwen2.5-1.5B-Instruct-Q4_K_M.gguf`

The model is run locally using llama.cpp.

The model file is not included in this repository.

## Local LLM Connection

The Python application communicates with the local llama.cpp server through:

`http://localhost:8080/completion`

The expected setup is:

Python Agent
    |
    | HTTP request
    v
llama.cpp Server
    |
    v
Qwen2.5 GGUF Model

Therefore, cloning this repository alone is not sufficient to run the
complete application.

The user must separately set up llama.cpp and a compatible Qwen2.5 GGUF model,
then start the local server at the expected endpoint.

## Requirements

- Python 3.x
- llama.cpp
- Qwen2.5-1.5B-Instruct GGUF model

Install the Python dependency with:

```bash
pip install -r requirements.txt