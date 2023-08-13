# ai-docs-engine
`ai-docs-engine` is an experimental tool which automatically generates and inserts [docstring](https://en.wikipedia.org/wiki/Docstring) comments for entire codebases. 

## Features
- Pre-existing docstrings always take priority and are **never** over-written. 
- Locally cache all API calls to avoid paying for same call more than once; uses `diskcache` and `SQLite3`. 
- LLM agnostic; bring your own model by simply implementing and passing a callable with the required signature. OpenAI API is used by default. 

## Limitations, Recommendations
- Docstrings may lack context and therefore be inaccurate **[0]**. 
- I believe this tool will work best to "fill in the gaps" for a codebase which currently lacks docstrings. 
- I do not suggest using this tool in a professional/production environment. 

## Planned
- [ ] **[0]** I am looking into using more OpenAI [function calls](https://platform.openai.com/docs/guides/gpt/function-calling) to enable stronger reasoning by allowing the LLM to request definitions of code referenced in target function/class. 
- [ ] Improve concurrency support and handle OpenAI rate limits [properly](https://github.com/openai/openai-cookbook/blob/main/examples/api_request_parallel_processor.py). 

## Supported Languages
### Current
- [x] Python
### Planned
- [ ] C++
- [ ] Java
- [ ] JavaScript / TypeScript

## License
Licensed under the [MIT license](https://github.com/williampettit/ai-docs-engine/blob/main/LICENSE.md).
