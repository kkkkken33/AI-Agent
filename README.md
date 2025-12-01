<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a id="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->


<!-- PROJECT LOGO -->
<br />
<div align="center">
  <img src="image/Hong_Kong_University_of_Science_and_Technology_symbol.png" alt="Logo" width="80" height="">

<h3 align="center">Final Project</h3>

  <p align="center">
    The final project of course AIAA3102 (L02) - Python Programming for Artificial Intelligence
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

This project implements a **ReAct (Reasoning and Acting) Agent** framework that combines large language models with external tools to answer complex queries through iterative reasoning and action execution. Built as the Final Project B for AIAA3102 - Python Programming for Artificial Intelligence, it demonstrates advanced AI agent design patterns including:

* **Multi-step Reasoning**: The agent breaks down complex questions into logical steps using chain-of-thought prompting
* **Tool Integration**: Seamlessly connects to search engines, calculators, weather APIs, and knowledge bases
* **Security Features**: Implements prompt injection detection, input sanitization, and output validation
* **Structured Output**: Uses Pydantic models to ensure type-safe responses from LLMs
* **Configurable Pipeline**: YAML-based configuration for model parameters, tool selection, and execution limits

The agent follows the ReAct paradigm where each iteration consists of:
1. **Thought** - Reasoning about what information is needed
2. **Action** - Executing a tool to gather that information  
3. **Observation** - Processing the tool's output
4. **Answer** - Providing the final response when sufficient information is collected

This architecture enables the system to handle diverse queries ranging from factual lookups to multi-step calculations while maintaining security and reliability through built-in safeguards.


<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* [![Python][Python]][Python-url]
* [![Ollama][Ollama]][Ollama-url]
* [![Wikipedia API][Wikipedia]][Wikipedia-url]




<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

To set up the ReAct Agent locally, follow these steps to configure the environment and install dependencies.

### Prerequisites

Ensure you have the following installed on your system:

* **Python 3.8+**
  ```sh
  python --version
  ```

* **Ollama** (for running local LLMs)
  ```sh
  # Install Ollama from https://ollama.com/download
  # Pull required models
  ollama pull gemma3:4b
  ollama pull qwen3:8b
  ```
  For more available model and information, see ollama's website (https://ollama.com/search)

* **pip** (Python package manager)
  ```sh
  python -m pip install --upgrade pip
  ```

### Installation

1. **Clone the repository**
   ```sh
   git clone https://github.com/your_username/react-agent.git
   cd react-agent
   ```

2. **Create a virtual environment** (recommended)
   ```sh
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install required packages**
   ```sh
   pip install -r requirements.txt
   ```
   
   Key dependencies include:
   - `ollama` - LLM interface
   - `pydantic` - Data validation
   - `pyyaml` - Configuration management
   - `python-weather` - Weather data
   - `wikipedia-api` - Knowledge base access

4. **Configure the agent**
   
   Edit `config.yaml` to customize model parameters and tool settings:
   ```yaml
   model:
     agent_model_name: "llama3"
     temperature: 0.2
   
   agent:
     max_steps: 10
     use_planner: true
   
   input:
     user_input: "What is the weather in New York?"
   ```

5. **Run the agent**
   ```sh
   python main.py
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- TOOL SPECIFICATIONS -->
## Tool Specifications

The ReAct Agent integrates multiple tools to handle diverse query types. Each tool is designed for specific tasks and can be invoked through natural language actions.

### Available Tools

#### 1. **Search Tool** (`search`)
Retrieves information from the knowledge base or external sources.

**Syntax:**
```
Action: search("query string")
```

**Features:**
- Local knowledge base lookup (birthdays, cities, facts)
- Wikipedia API integration for general knowledge (Not use by default. You need to configure in `config.yaml`)
- Websearch by ollama api for any latest information (Not use by default. You need to configure in `config.yaml`)

**Example:**
```
Action: search("Obama's birthday")
Observation: August 4, 1961
```
**Advanced Features for search tool**

#### External Search Integration

The agent supports two external search capabilities that can be enabled through configuration.

#### Wikipedia Search (Optional)

Enable Wikipedia API for broader knowledge base access:

1. **Configure user agent** in `config.yaml`:
   ```yaml
   api:
     wiki_user_agent: "HWAI-SearchAgent-Bot/0.1 (contact: your_email@example.com)"
   
   tools:
     use_wikipedia_search: true
   ```

2. **Usage**: The search tool automatically queries Wikipedia when local knowledge base has no results
   ```
   Action: search("Python programming language history")
   Observation: Python was created by Guido van Rossum and first released in 1991...
   ```

**Note**: Follow Wikipedia's [API etiquette](https://foundation.wikimedia.org/wiki/Policy:Wikimedia_Foundation_User-Agent_Policy) by providing a valid user agent with contact information.

---

#### Ollama Web Search (Optional)

Enable real-time internet search through Ollama's web search capability:

1. **Set API key** in `config.yaml`:
   ```yaml
   api:
     OLLAMA_API_KEY: "your_ollama_api_key_here"
   
   tools:
     use_internet_search: true
   ```
    For local usage, you must add your `OLLAMA_API_KEY` to your system environment variables:
  
    **Windows:**
    ```cmd
    setx OLLAMA_API_KEY "your_api_key_here"
    ```
    
    **macOS/Linux:**
    ```bash
    export OLLAMA_API_KEY="your_api_key_here"
    # Add to ~/.bashrc or ~/.zshrc for persistence
    echo 'export OLLAMA_API_KEY="your_api_key_here"' >> ~/.bashrc
    ```

2. **Usage**: The search tool will query the internet for up-to-date information
   ```
   Action: search("current weather forecast New York")
   Observation: [Real-time web results from Ollama]
   ```

3. **Obtain API key**:
   - Visit [Ollama's website](https://ollama.com/)
   - Sign up for an account
   - Generate an API key from your dashboard (https://ollama.com/settings/keys)

---

#### Hotel Price Lookup (Optional)

For travel planning queries, enable hotel price search:
1. **Obtain an API key**
   Rigister and get an api key at https://www.makcorps.com/

2. **Configure Makcorps API** in `config.yaml`:
   ```yaml
   api:
     MAKCORPS_API_KEY: "your_makcorps_jwt_token"
   
   tools:
     use_hotel_price_lookup: true
   ```

3. **Usage**:
   ```
   Action: search(london)
   Observation: [Hotel price comparison data]
   ```

**Security Note**: Never commit API keys to version control. Use environment variables or a separate `.env` file:

```python
import os
api_key = os.getenv("OLLAMA_API_KEY")
```
---

#### 2. **Calculator Tool** (`calc`)
Evaluates mathematical expressions safely using AST parsing.

**Syntax:**
```
Action: calc("mathematical expression")
```

**Supported Operations:**
- Basic arithmetic: `+`, `-`, `*`, `/`, `//`, `%`
- Exponentiation: `**`
- Parentheses for grouping
- Multiple operations in one expression

**Example:**
```
Action: calc("(2025 - 1961) + (2025 - 1946)")
Observation: 143
```

---

#### 3. **Weather Tool** (`weather`)
Fetches current weather and 3-day forecasts for any city.

**Syntax:**
```
Action: weather("City Name")
```

**Returns:**
- Current temperature
- Daily forecasts with high/low temperatures
- Weather descriptions

**Example:**
```
Action: weather("Leshan")
Observation: Weather for Leshan:
Date: 2025-11-30; Temperature: 58 degree Fahrenheit
Date: 2025-12-01; Temperature: 58 degree Fahrenheit
Date: 2025-12-02; Temperature: 57 degree Fahrenheit
```

---

### Tool Registration

Tools are registered in `tool_registry` and can be easily extended:

```python
tool_registry = {
    "search": search_tool,
    "calc": calculator_tool,
    "weather": get_weather_tool,
}
```

### Adding Custom Tools

To add a new tool:

1. Define the tool function in `tools.py`:
   ```python
   def my_custom_tool(input_param):
       # Tool logic here
       return result
   ```

2. Register it in `main.py`:
   ```python
   tool_registry["my_tool"] = my_custom_tool
   ```

3. Update the system prompt to include the new tool description

<p align="right">(<a href="#readme-top">back to top</a>)</p>





<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Top contributors:

<a href="https://github.com/github_username/repo_name/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=github_username/repo_name" alt="contrib.rocks image" />
</a>




<!-- CONTACT -->
## Contact

Chang XU - cxu475@connect.hkust-gz.edu.cn

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* []()
* []()
* []()

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/github_username/repo_name.svg?style=for-the-badge
[contributors-url]: https://github.com/github_username/repo_name/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/github_username/repo_name.svg?style=for-the-badge
[forks-url]: https://github.com/github_username/repo_name/network/members
[stars-shield]: https://img.shields.io/github/stars/github_username/repo_name.svg?style=for-the-badge
[stars-url]: https://github.com/github_username/repo_name/stargazers
[issues-shield]: https://img.shields.io/github/issues/github_username/repo_name.svg?style=for-the-badge
[issues-url]: https://github.com/github_username/repo_name/issues
[license-shield]: https://img.shields.io/github/license/github_username/repo_name.svg?style=for-the-badge
[license-url]: https://github.com/github_username/repo_name/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/linkedin_username
[product-screenshot]: images/screenshot.png
<!-- Shields.io badges. You can a comprehensive list with many more badges at: https://github.com/inttter/md-badges -->
[Next.js]: https://img.shields.io/badge/next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white
[Next-url]: https://nextjs.org/
[React.js]: https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB
[React-url]: https://reactjs.org/
[Vue.js]: https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D
[Vue-url]: https://vuejs.org/
[Angular.io]: https://img.shields.io/badge/Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white
[Angular-url]: https://angular.io/
[Svelte.dev]: https://img.shields.io/badge/Svelte-4A4A55?style=for-the-badge&logo=svelte&logoColor=FF3E00
[Svelte-url]: https://svelte.dev/
[Laravel.com]: https://img.shields.io/badge/Laravel-FF2D20?style=for-the-badge&logo=laravel&logoColor=white
[Laravel-url]: https://laravel.com
[Bootstrap.com]: https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white
[Bootstrap-url]: https://getbootstrap.com
[JQuery.com]: https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white
[JQuery-url]: https://jquery.com 
[Ollama]: https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=shadcnui&logoColor=white
[Ollama-url]: https://ollama.com/
[Wikipedia]: https://img.shields.io/badge/Wikipedia%20API-4d8ccb?style=for-the-badge&logo=wikipedia&logoColor=white
[Wikipedia-url]: https://www.mediawiki.org/wiki/API:Main_page
[Python]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://www.python.org/