import re
from prompt import AGENT_SYSTEM_PROMPT, JUDGEMENTMODEL_SYSTEM_PROMPT
from utils import query_llm, judge_llm, security_llm
from tools import search_tool, calculator_tool, get_weather_tool, plan_tool
from utils import PromptInjectionFilter, OutputValidator
from pydantic import BaseModel
from typing import Literal, Optional
from utils import Response, Action
import yaml

# Load Configuration
def load_config(path="config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

cfg = load_config()
max_steps = cfg["agent"]["max_steps"]
output_file = cfg["output"]["log_file"]
use_planner = cfg["tools"]["use_planner"]
user_input = cfg["input"]["user_input"]
use_judgement_model = cfg["tools"]["use_judgement_model"]

with open(output_file, "w", encoding="utf-8") as f:
    f.write("Agent Execution Log\n")
    f.write("="*50 + "\n")

tool_map = {
    "search_tool": search_tool,
    "calculator_tool": calculator_tool,
    "get_weather_tool": get_weather_tool,
    "plan_tool": plan_tool,
}

tool_registry = {
    name: tool_map[func_name] 
    for name, func_name in cfg["tools"]["tool_registry"].items()
    if func_name in tool_map
}





# Real ReAct Agent Loop
def run_real_react_agent(question, max_steps=10, use_planner=False, use_judgement_model=False):
    history = f"Question: {question}\n"
    print(f"Starting Real ReAct Agent for: {question}")
    print("="*50)

    if use_planner:
        plan = plan_tool(f"Provide a step-by-step plan to answer the question: {question}")
        print(f"[Planner]: Step by step plan: \n {plan}\n")
        history += f"Step by step plan: \n {plan}\n"

    count = 0
    # plan = plan_tool(f"Provide a step-by-step plan to answer the question: {question}")
    # history += f"[Step by step plan] {plan}\n"
    # with open(output_file, "a", encoding="utf-8") as f:
    #     f.write(history)
    #     f.write("="*50 + "\n")
    while count < max_steps:
        count += 1
        # 1. Call LLM (Stop at Observation to let tool run)
        json_response = query_llm(history, stop_sequences=["Observation:"], system_msg=AGENT_SYSTEM_PROMPT)
        try:
            response = Response.model_validate_json(json_response)
        except (ValueError, Exception) as e:
            print(f"[Error] Failed to parse LLM response: {e}")
            print(f"[Debug] Raw response: {json_response}")
            history += "Observation: Error: LLM returned invalid format. Please try again.\n"
            continue
        
        if response.action is not None:
            print(f"[LLM]: Thought: {response.thought} \n Action: {response.action.tool} : {response.action.input}")
            history += "Thought: " + response.thought + "\n"+ "Action: " + response.action.tool + " :" + f"({response.action.input})\n"
        else:
            print(f"[LLM]: Thought: {response.thought} \n")
            history += "Thought: " + response.thought + "\n"

        # 2. Check for Final Answer
        if response.final_answer is not None:
            history += f"Final Answer: {response.final_answer}\n"
            print(f"[LLM]: Final Answer: {response.final_answer}")
            if use_judgement_model:
                judgement = judge_llm(history, system_msg=JUDGEMENTMODEL_SYSTEM_PROMPT)
                print(f"[Judgement]: {judgement}")
                use_judgement_model = False  # Only judge once per final answer
                with open(output_file, "a", encoding="utf-8") as f:
                    if output_validator.validate_output(response.final_answer):
                        print("[Output Validation]: Passed")
                        f.write("Output Validation: Passed\n")
                    else:
                        print("[Output Validation]: Failed")
                        f.write("Output Validation: Failed\n")
                        raise ValueError("[Warning] Detected sensitive output. Aborting.")
                    f.write(history)
                    f.write(f"Judgement: {judgement}\n")
                    f.write("="*50 + "\n")
                if "Incorrect" in judgement:
                    judgement = judgement.replace("Incorrect", "").strip()
                    history = f"Question: {question}\n Hint: {judgement}"
                    # plan = plan_tool(f"Provide a step-by-step plan to answer the question: {question}")
                    # history += f"[Step by step plan] {plan}\n"
                    # print(f"[Debug] History: {history}")
                    count = 0
                    continue
                else:
                    return response.final_answer, count
            else:
                with open(output_file, "a", encoding="utf-8") as f:
                    if output_validator.validate_output(response.final_answer):
                        print("[Output Validation]: Passed")
                        f.write("Output Validation: Passed\n")
                    else:
                        print("[Output Validation]: Failed")
                        f.write("Output Validation: Failed\n")
                        raise ValueError("[Warning] Detected sensitive output. Aborting.")
                    f.write(history)
                    f.write("="*50 + "\n")
                return response.final_answer, count

        # 3. Parse Action
        if response.action is not None:
            tool_name = response.action.tool
            tool_arg = response.action.input
            # print(f"[Debug] Invoking Tool: {tool_name} with Arg: {tool_arg}")
            if tool_name in tool_registry:
                observation =tool_registry[tool_name](tool_arg)
                print(f"[Obs]: {observation}")
                history += f"Observation: {observation}\n"
            else:
                print(f"[Obs]: Error: Tool not found.")
                history += "Observation: Error: Tool not found.\n"
        # print(f"[Debug] Current History:\n{history}")
    with open(output_file, "a", encoding="utf-8") as f:
        f.write(history)
        f.write("Timed out\n")
        f.write("="*50 + "\n")
    return "Timed out", count

# Prompt Injection Detection and Sanitization
prompt_filter = PromptInjectionFilter()
if prompt_filter.detect_injection(user_input):
    print("[Warning] Potential prompt injection detected. Aborting request.")
    raise ValueError("Potential prompt injection detected.")
user_input = prompt_filter.sanitize_input(user_input)

# Security Intent Classification
security_classification = "Passed" if "unsafe" not in security_llm(user_input) else "Failed"
print(f"[Security Classification]: {security_classification}")
if security_classification == "Failed":
    print("[Warning] Unsafe user intent detected. Aborting request.")
    raise ValueError("Unsafe user intent detected.")

# Output Validation Setup
output_validator = OutputValidator()
# Run the Real ReAct Agent
result, count = run_real_react_agent(user_input, max_steps=max_steps, use_planner=use_planner, use_judgement_model=use_judgement_model)
print("="*50)
with open(output_file, "a", encoding="utf-8") as f:
    f.write("="*50 + "\n")
    f.write(f"FINAL RESULT: {result}\n")
print(f"FINAL RESULT: {result}")