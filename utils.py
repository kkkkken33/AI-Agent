from ollama import chat
from ollama import ChatResponse
from prompt import AGENT_SYSTEM_PROMPT
from prompt import JUDGEMENTMODEL_SYSTEM_PROMPT
from prompt import PLANNER_SYSTEM_PROMPT
from prompt import SECURITY_SYSTEM_PROMPT
import re
from pydantic import BaseModel
from typing import Literal, Optional
import yaml

# load_config
def load_config(path="config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

cfg = load_config()
agent_model_name = cfg["model"]["agent_model_name"]
agent_model_temperature = cfg["model"]["agent_model_temperature"]
judgement_model_name = cfg["model"]["judgement_model_name"]
judgement_model_temperature = cfg["model"]["judgement_model_temperature"]
planner_model_name = cfg["model"]["planner_model_name"]
planner_model_temperature = cfg["model"]["planner_model_temperature"]

def query_llm(prompt, stop_sequences=None, system_msg=AGENT_SYSTEM_PROMPT, temperature=agent_model_temperature):
    try:
        response: ChatResponse = chat(model=agent_model_name, messages=[
                {
                    'role': 'system',
                    'content': system_msg,
                },
                {
                    'role': 'user',
                    'content': prompt,
                },
            ],
            options={
                'temperature': temperature,
                'stop': stop_sequences,
            },  
            format=Response.model_json_schema(),
        )
        # print(response['message']['content'])
        # or access fields directly from the response object
        return response.message.content
    except Exception as e:
        return f"Error: {str(e)}"
    
def judge_llm(prompt, stop_sequences=None, system_msg=JUDGEMENTMODEL_SYSTEM_PROMPT, temperature=judgement_model_temperature):
    try:
        response: ChatResponse = chat(model=judgement_model_name, messages=[
                {
                    'role': 'system',
                    'content': system_msg,
                },
                {
                    'role': 'user',
                    'content': prompt,
                },
            ],
            options={
                'temperature': temperature,
                'stop': stop_sequences,
            },  
            think = True,
            # temperature=temperature,
            # stream=True,
        )
        # print(response['message']['content'])
        # or access fields directly from the response object
        return response.message.content
    except Exception as e:
        return f"Error: {str(e)}"

def plan_llm(prompt, stop_sequences=None, system_msg=PLANNER_SYSTEM_PROMPT, temperature=planner_model_temperature):
    try:
        response: ChatResponse = chat(model=planner_model_name, messages=[
                {
                    'role': 'system',
                    'content': system_msg,
                },
                {
                    'role': 'user',
                    'content': prompt,
                },
            ],
            options={
                'temperature': temperature,
                'stop': stop_sequences,
            },  
            think = True,
            # temperature=temperature,
            # stream=True,
        )
        # print(response['message']['content'])
        # or access fields directly from the response object
        return response.message.content
    except Exception as e:
        return f"Error: {str(e)}"
    
# Ref: https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html
class PromptInjectionFilter:
    def __init__(self):
        self.dangerous_patterns = [
            r'ignore\s+(all\s+)?previous\s+instructions?',
            r'you\s+are\s+now\s+(in\s+)?developer\s+mode',
            r'system\s+override',
            r'reveal\s+prompt',
        ]

        # Fuzzy matching for typoglycemia attacks
        self.fuzzy_patterns = [
            'ignore', 'bypass', 'override', 'reveal', 'delete', 'system'
        ]

    def detect_injection(self, text: str) -> bool:
        # Standard pattern matching
        if any(re.search(pattern, text, re.IGNORECASE)
               for pattern in self.dangerous_patterns):
            return True

        # Fuzzy matching for misspelled words (typoglycemia defense)
        words = re.findall(r'\b\w+\b', text.lower())
        for word in words:
            for pattern in self.fuzzy_patterns:
                if self._is_similar_word(word, pattern):
                    return True
        return False

    def _is_similar_word(self, word: str, target: str) -> bool:
        """Check if word is a typoglycemia variant of target"""
        if len(word) != len(target) or len(word) < 3:
            return False
        # Same first and last letter, scrambled middle
        return (word[0] == target[0] and
                word[-1] == target[-1] and
                sorted(word[1:-1]) == sorted(target[1:-1]))

    def sanitize_input(self, text: str) -> str:
        # Normalize common obfuscations
        text = re.sub(r'\s+', ' ', text)  # Collapse whitespace
        text = re.sub(r'(.)\1{3,}', r'\1', text)  # Remove char repetition

        for pattern in self.dangerous_patterns:
            text = re.sub(pattern, '[FILTERED]', text, flags=re.IGNORECASE)
        return text[:10000]  # Limit length
    
class OutputValidator:
    def __init__(self):
        self.suspicious_patterns = [
            r'SYSTEM\s*[:]\s*You\s+are',     # System prompt leakage
            r'API[_\s]KEY[:=]\s*\w+',        # API key exposure
            r'instructions?[:]\s*\d+\.',     # Numbered instructions
        ]

    def validate_output(self, output: str) -> bool:
        return not any(re.search(pattern, output, re.IGNORECASE)
                      for pattern in self.suspicious_patterns)

    def filter_response(self, response: str) -> str:
        if not self.validate_output(response) or len(response) > 5000:
            return "I cannot provide that information for security reasons."
        return response
    
def security_llm(prompt, stop_sequences=None, system_msg=SECURITY_SYSTEM_PROMPT, temperature=0):
    try:
        response: ChatResponse = chat(model='gemma3:4b', messages=[
                {
                    'role': 'system',
                    'content': system_msg,
                },
                {
                    'role': 'user',
                    'content': prompt,
                },
            ],
            options={
                'temperature': temperature,
                'stop': stop_sequences,
            },  
            # think = True,
            # temperature=temperature,
            # stream=True,
        )
        # print(response['message']['content'])
        # or access fields directly from the response object
        return response.message.content
    except Exception as e:
        return f"Error: {str(e)}"
    
class Action(BaseModel):
    tool: Literal["search", "calc", "weather"]
    input: str

class Response(BaseModel):
    thought: str
    action: Optional[Action] = None
    final_answer: Optional[str] = None


if __name__ == "__main__":
    query_llm("Who are you?")
