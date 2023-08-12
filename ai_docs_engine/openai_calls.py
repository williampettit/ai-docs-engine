import diskcache
import openai

from .utilities import col


# Config
OPENAI_MODEL_TO_USE = "gpt-3.5-turbo-0613"


# Cache all OpenAI API calls to avoid paying for same call more than once
cache = diskcache.Cache("data/cache/openai_calls")


@cache.memoize()
def generate_docstring_with_openai(definition: str, definition_type: str) -> str:
  assert isinstance(definition, str), "Expected definition to be a string"
  assert isinstance(definition_type, str), "Expected definition_type to be a string"
  assert definition_type in ["function", "class"], "Expected definition_type to be either 'function' or 'class'"

  # Generate docstring with OpenAI API
  response = openai.ChatCompletion.create(
    model=OPENAI_MODEL_TO_USE,
    messages=[
      {
        "role": "system",
        "content": f"""Describe what this Python {definition_type} does.
Limit your description to 1 sentence; pretend that it is going to be used as a comment within a codebase.
Your description should begin with a verb, and should not include the {definition_type} name itself in the description.

Example output:
Creates a matrix of given shape and propagates it with random samples from a uniform distribution.""",
      },
      {
        "role": "user",
        "content": definition,
      },
    ],
  )

  docstring = response["choices"][0]["message"]["content"]

  print(col(f"Generated docstring for {definition_type}:", "green"), docstring, "\n")

  return docstring
