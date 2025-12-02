from ollama import chat
import pprint
import wikipedia
import wikipediaapi
import ollama
from prompt import AGENT_SYSTEM_PROMPT

knowledge_base = {
    "obama": "August 4, 1961",
    "barack obama": "August 4, 1961",
    "trump": "June 14, 1946",
    "donald trump": "June 14, 1946",
    "city": "Chengdu",
    "user's city": "Chengdu",
    "current date": "2025",
    "near guangzhou": "Foshan, Shenzhen, Dongguan",
    "from guangzhou": "Foshan, Shenzhen, Dongguan",
    "near chengdu": "Leshan, Emeishan, Dujiangyan",
    "from chengdu": "Leshan, Emeishan, Dujiangyan",
    "python release date": "February 20, 1991",
    "hotel": "600 CNY per night",
    "destinations": "Foshan, Shenzhen, Dongguan",
}

def search_tool(query: str, use_internet: bool = False, use_wikipedia: bool = False) -> str:
    """Local/Wikipedia/Ollama 搜索工具"""
    normalized = query.lower().replace('"', '').strip()
    print(f"   [System] Searching for: '{normalized}'")

    # 先查本地知识库
    for key, value in knowledge_base.items():
        if key in normalized:
            return value

    if not use_internet and not use_wikipedia:
        return "Not found in local database."

    if use_wikipedia:
        try:
            results = wikipedia.search(normalized)
            if not results:
                return "No matching wikipedia page."

            wiki = wikipediaapi.Wikipedia(
                language="en",
                user_agent="HWAI-SearchAgent-Bot/0.1 (contact: your_email@example.com)"
            )
            page = wiki.page(results[0])
            return page.summary[:500]
        except wikipedia.DisambiguationError as e:
            if e.options:
                try:
                    page = wikipedia.page(e.options[0])
                    return page.summary[:500]
                except Exception:
                    return "Wikipedia disambiguation failed."
            return "Ambiguous Wikipedia query."
        except wikipedia.PageError:
            return "Wikipedia page not found."
        except Exception as exc:
            return f"Wikipedia error: {exc}"

    if use_internet:
        response = ollama.web_search(normalized, max_results=3)
        return pprint.pformat(response, width=80, compact=False)

    return "Search failed."

# Ollama tool schema
ollama_search_tool = {
    "type": "function",
    "function": {
        "name": "search_tool",
        "description": "Search local KB, Wikipedia, or via Ollama web search.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query."
                },
                "use_internet": {
                    "type": "boolean",
                    "description": "Enable Ollama web search.",
                    "default": False
                },
                "use_wikipedia": {
                    "type": "boolean",
                    "description": "Enable Wikipedia search.",
                    "default": False
                }
            },
            "required": ["query"]
        }
    }
}

def get_temperature(city: str) -> str:
  """Get the current temperature for a city
  
  Args:
    city: The name of the city

  Returns:
    The current temperature for the city
  """
  temperatures = {
    "New York": "22°C",
    "London": "15°C",
    "Tokyo": "18°C",
  }
  return temperatures.get(city, "Unknown")

messages = [
    {"role": "system", "content": "You are a helpful assistant that uses tool calls to answer user questions. You should output Thought-Action-Observation sequences until you find the final answer."},
    {"role": "user", "content": "How older is Trump than Obama?"}]

# pass functions directly as tools in the tools list or as a JSON schema
response = chat(model="qwen3:8b", messages=messages, tools=[get_temperature, ollama_search_tool], think=True)

messages.append(response.message)
if response.message.tool_calls:
  # only recommended for models which only return a single tool call
  call = response.message.tool_calls[0]
  result = get_temperature(**call.function.arguments)
  # add the tool result to the messages
  messages.append({"role": "tool", "tool_name": call.function.name, "content": str(result)})

  response = chat(model="qwen3:8b", messages=messages, tools=[get_temperature], think=True)
print(response.message.content)