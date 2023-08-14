# ai-docs-engine
`ai-docs-engine` is an experimental tool which automatically generates and inserts [docstring](https://en.wikipedia.org/wiki/Docstring) comments for entire codebases. 

https://github.com/williampettit/ai-docs-engine/assets/14142910/4638bf5b-da24-45d3-a413-93dff0591db1

## Features
- Pre-existing docstrings always take priority and are **never** over-written. 
- Locally cache all API calls to avoid paying for same call more than once; uses `diskcache` which is just a local `SQLite3` database that can be queried standalone later on. 
- LLM agnostic; bring your own model by simply implementing and passing a callable with the required signature. OpenAI API is used by default. 

## Limitations, Recommendations
- Docstrings may lack context and therefore be inaccurate [[0]](#planned). 
- I believe this tool will work best to "fill in the gaps" for a codebase which currently lacks docstrings. 
- I do not suggest using this tool in a professional/production environment. 

## Planned Features, Notes
- [ ] [[0]](#limitations-recommendations) I am looking into using more OpenAI [function calls](https://platform.openai.com/docs/guides/gpt/function-calling) to enable stronger reasoning by allowing the LLM to request definitions of code referenced in target function/class. 
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
