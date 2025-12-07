<!-- BILL OF MATERIALS -->
## Bill of Materials

This project utilizes the following open-source libraries, frameworks, and pretrained models:

### Core Dependencies

| Library | Version | License | Purpose | Citation |
|---------|---------|---------|---------|----------|
| **Ollama** | 0.6.1 | MIT | Local LLM inference framework | [Ollama](https://ollama.com/) |
| **Pydantic** | 2.12.5 | MIT | Data validation and structured outputs | [Pydantic Documentation](https://docs.pydantic.dev/) |
| **PyYAML** | 6.0.3 | MIT | YAML configuration file parsing | [PyYAML](https://pyyaml.org/) |

### Search & Knowledge Base

| Library | Version | License | Purpose | Citation |
|---------|---------|---------|---------|----------|
| **Wikipedia** | 1.4.0 | MIT | Python Wikipedia API wrapper | [wikipedia-python](https://github.com/goldsmith/Wikipedia) |
| **Wikipedia-API** | 0.8.1 | MIT | Advanced Wikipedia data access | [Wikipedia-API](https://github.com/martin-majlis/Wikipedia-API) |
| **Requests** | 2.32.5 | Apache 2.0 | HTTP library for API calls | [Requests](https://requests.readthedocs.io/) |

### Weather Integration

| Library | Version | License | Purpose | Citation |
|---------|---------|---------|---------|----------|
| **python-weather** | 2.1.0 | MIT | Asynchronous weather data API | [python-weather](https://github.com/null8626/python-weather) |
| **aiohttp** | 3.11.0+ | Apache 2.0 | Async HTTP client/server | [aiohttp](https://docs.aiohttp.org/) |

### Type System & Utilities

| Library | Version | License | Purpose | Citation |
|---------|---------|---------|---------|----------|
| **typing_extensions** | 4.15.0 | PSF | Backported type hints for Python < 3.10 | [typing_extensions](https://github.com/python/typing_extensions) |

### Pretrained Models

| Model | Provider | Size | Purpose | Access |
|-------|----------|------|---------|--------|
| **Llama 3.1** | Meta AI | 8B parameters | Agent reasoning & tool execution | Via Ollama: `ollama pull llama3.1:8b` |
| **Qwen 3** | Alibaba Cloud | 8B parameters | Planning & judgement tasks | Via Ollama: `ollama pull qwen3:8b` |
| **Gemma 3** | Google | 4B parameters | Security classification | Via Ollama: `ollama pull gemma3:4b` |

### Security Framework Reference

| Resource | Author/Organization | Purpose | Citation |
|----------|---------------------|---------|----------|
| **LLM Prompt Injection Prevention Cheat Sheet** | OWASP | Security pattern implementation | [OWASP Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html) |

### Development Tools (Not in Runtime)

- **Python** 3.8+ - PSF License
- **Git** - GPL v2
- **Visual Studio Code** - MIT License

---

### License Compliance

All dependencies are distributed under permissive open-source licenses (MIT, Apache 2.0, PSF) that allow:
- ✅ Commercial use
- ✅ Modification
- ✅ Distribution
- ✅ Private use

**No GPL-licensed dependencies** are used in the runtime environment to avoid copyleft restrictions.

### Model Citations

**Llama 3.1:**
```
@misc{llama3,
  title={Llama 3.1: Open Foundation and Fine-Tuned Language Models},
  author={Meta AI},
  year={2024},
  url={https://ai.meta.com/blog/meta-llama-3-1/}
}
```

**Qwen 3:**
```
@misc{qwen3,
  title={Qwen Technical Report},
  author={Alibaba Cloud},
  year={2024},
  url={https://github.com/QwenLM/Qwen}
}
```

**Gemma:**
```
@misc{gemma,
  title={Gemma: Open Models Based on Gemini Research and Technology},
  author={Google DeepMind},
  year={2024},
  url={https://ai.google.dev/gemma}
}
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>