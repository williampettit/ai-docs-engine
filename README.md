# ai-docs-engine
`ai-docs-engine` is an experimental tool which automatically generates and inserts [docstring](https://en.wikipedia.org/wiki/Docstring) comments for your entire codebase. 

## Features
- Pre-existing docstrings always take priority and are **never** over-written. 
- Caches all OpenAI API calls to avoid paying for same call more than once. 
- LLM agnostic; you can bring your own model by simplying passing a custom callable. OpenAI API is used by default. 

## Limitations, Recommendations
- Docstrings may lack context and therefore be inaccurate. **[0]**
- I believe this tool will work best to "fill in the gaps" for a codebase which currently lacks docstrings. 
- I do not suggest using this tool in a professional/production environment. 

## Planned
- **[0]** I am looking into possibly using OpenAI `function calls` to enable better reasoning by allowing the LLM to request definitions of code referenced in target function/class. 
- Improve concurrency support. 
- Handle OpenAI rate limits properly. 

## Language Support
### Current
- [x] Python
### Planned
- [ ] C++
- [ ] Java
- [ ] JavaScript / TypeScript

## License
Licensed under the [MIT license](https://github.com/williampettit/ai-docs-engine/blob/main/LICENSE.md).
