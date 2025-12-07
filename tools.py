import ast
import operator
import os
import pprint
import asyncio
import python_weather
# from googleapiclient.discovery import build
import ollama
from utils import plan_llm
import json
import requests
import wikipedia
import wikipediaapi
import yaml

# Load configurations
def load_config(path="config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
cfg = load_config()
MAKCORPS_API_KEY = cfg["api"]["MAKCORPS_API_KEY"]
use_wikipedia_search = cfg["tools"]["use_wikipedia_search"]
use_internet_search = cfg["tools"]["use_internet_search"]
wiki_user_agent = cfg["api"]["wiki_user_agent"]

# 1. Setup Knowledge Base (Matching the Slide's Facts)
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

# 2. Define Tools
def search_tool(query, use_internet=use_internet_search, use_wikipedia=use_wikipedia_search, wiki_user_agent=wiki_user_agent):
    query = query.lower().replace('"', '').strip()
    print(f"   [System] Searching for: '{query}'")
    # Simple fuzzy match
    for k, v in knowledge_base.items():
        if k in query:
            return v
    if use_internet == False and use_wikipedia == False:
        return "Not found in local database."
    elif use_wikipedia:
        try:
            # Step 1: search first
            results = wikipedia.search(query)
            print(f"[DEBUG] Wikipedia search results: {results}")
            if not results:
                return "No matching wikipedia page."
            
            # Step 2: fetch the first page
            try:
                print(f"[DEBUG] Fetching Wikipedia page for: {results[0]}")
                wiki = wikipediaapi.Wikipedia(
                    language='en',
                    user_agent=wiki_user_agent
                )
                page = wiki.page(results[0])
                return page.summary[:500]
            
            except wikipedia.DisambiguationError as e:
                # pick a more specific page if ambiguous
                if e.options:
                    try:
                        page = wikipedia.page(e.options[0])
                        return page.summary[:500]
                    except Exception:
                        return "Wikipedia disambiguation failed."
                return "Ambiguous Wikipedia query."

        except wikipedia.PageError:
            return "Wikipedia page not found."
        except Exception as e:
            return f"Error: {e}"
    elif use_internet:
        response = ollama.web_search("Joe Biden birthdate", max_results=3)
        formatted = pprint.pformat(response, width=80, compact=False)
        return formatted
        

def _safe_eval_expr(expression: str) -> str:
    ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }
    
    # Safe functions whitelist
    safe_functions = {
        'abs': abs,
        'round': round,
        'min': min,
        'max': max,
        'sum': sum,
    }


    def _eval(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.UnaryOp) and type(node.op) in ops:
            return ops[type(node.op)](_eval(node.operand))
        if isinstance(node, ast.BinOp) and type(node.op) in ops:
            return ops[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.Call):
            # Handle function calls like abs(), round(), etc.
            if isinstance(node.func, ast.Name) and node.func.id in safe_functions:
                func = safe_functions[node.func.id]
                args = [_eval(arg) for arg in node.args]
                return func(*args)
            raise ValueError(f"Unsupported function: {node.func.id if isinstance(node.func, ast.Name) else 'unknown'}")
        raise ValueError("Unsupported expression")

    tree = ast.parse(expression, mode="eval")
    return str(_eval(tree.body))

def calculator_tool(expression):
    print(f"   [System] Calculating: {expression}")
    try:
        return _safe_eval_expr(expression)
    except Exception:
        return "Error in calculation"

async def _fetch_weather(city, unit):
    async with python_weather.Client(unit=unit) as client:
        weather = await client.get(city)
        forecasts = f"Weather for {city}:\n".format(city=city)
        for daily in weather:
            forecasts += f"Date: {daily.date}; Temperature: {daily.temperature} degree Fahrenheit  \n"
        return forecasts if forecasts else "No weather data found."

def get_weather_tool(city, unit="imperial"):
    unit_map = {
        "imperial": python_weather.IMPERIAL,
        "metric": python_weather.METRIC,
    }
    selected_unit = unit_map.get(unit.lower(), python_weather.IMPERIAL)
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    return asyncio.run(_fetch_weather(city, selected_unit))

def plan_tool(task):
    return plan_llm(task)

def hotel_price_tool(city):
    # api_token = token or os.getenv("MAKCORPS_API_KEY")
    api_token = MAKCORPS_API_KEY
    if not api_token:
        return "Missing MAKCORPS_API_KEY."
    url = "https://api.makcorps.com/free/" + city.lower()
    headers = {
    'Authorization': f'JWT {api_token}',
    }
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            return f"API error {resp.status_code}: {resp.text}"
        return json.dumps(resp.json(), ensure_ascii=False, indent=2)
    except requests.RequestException as exc:
        return f"Request failed: {exc}"

if __name__ == "__main__":
    # Test search tool
    # print(search_tool("What is Obama's birthdate?"))
    # print(search_tool("When was Trump born?"))
    # print(search_tool("Who is Biden?"))

    # Test calculator tool
    print(calculator_tool("2025 - 1961"))
    print(calculator_tool("(1946 + 10)"))
    print(calculator_tool("100 / 0"))
    print(calculator_tool("2 * (3 + 5)"))
    print(calculator_tool("abs(1946 - 1961)"))  # → "15"
    print(calculator_tool("max(10, 20, 5)"))    # → "20"
    print(calculator_tool("round(3.14159, 2)")) # → "3.14"

    # google_api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    # print(f"Google API Key: {google_api_key}")
    # google_cse_id = "0167913e29a0a41ba"

    # def google_search(search_term, api_key, cse_id, **kwargs):
    #     service = build("customsearch", "v1", developerKey=api_key)
    #     res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    #     return res['items']

    # results = google_search(
    #     'hotel price in guangzhou', google_api_key, google_cse_id, num=10)
    # for result in results:
    #     pprint.pprint(result)

    
    # with open("ollama_response.txt", "w", encoding="utf-8") as f:
    #     f.write(formatted)

    # Test weather tool
    # print(get_weather_tool("Chengdu"))
    # print(hotel_price_tool("London"))

    # Test wikipedia search
    # print(search_tool("machine learning", use_wikipedia=True))