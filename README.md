# Mathematical Calculation Agent using Local LLM

A local LLM-based mathematical calculation agent developed as part of an
internship project at Bhabha Atomic Research Centre (BARC), Visakhapatnam.

The project combines a locally deployed language model with Python-based
mathematical tools to process natural-language mathematical problems,
generate a structured calculation plan, execute the calculation, and verify
the final result.

## Project Overview

The agent accepts mathematical problems written in natural language and
processes them through four stages:

1. Problem Refinement
2. Plan Generation
3. Plan Execution
4. Result Verification

The system uses a locally running Qwen2.5-1.5B-Instruct model through
llama.cpp.

## Architecture

```text
User Input
    |
    v
Problem Refinement
    |
    v
Plan Generation
    |
    v
Python Tool Execution
    |
    v
Result Verification
    |
    v
Final Answer