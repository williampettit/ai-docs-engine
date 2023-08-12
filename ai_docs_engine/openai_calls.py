import diskcache
import openai
import tiktoken
import logging

from .utilities import AIDocsEngineTooManyTokensError, col


# Config, TODO: move to CLI argument w/ this as default
DEFAULT_OPENAI_MODEL_TO_USE = "gpt-3.5-turbo-0613"
# DEFAULT_OPENAI_MODEL_TO_USE = "gpt-3.5-turbo-16k-0613"


# Cache all OpenAI API calls to avoid paying for same call more than once
cache = diskcache.Cache("data/cache/openai_calls")


# From: https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
def num_tokens_from_messages(messages, model):
  """
  Return the number of tokens used by a list of messages.
  """

  encoding = tiktoken.encoding_for_model(model)
  
  if model in {
    "gpt-3.5-turbo-0613",
    "gpt-3.5-turbo-16k-0613",
    "gpt-4-0314",
    "gpt-4-32k-0314",
    "gpt-4-0613",
    "gpt-4-32k-0613",
  }:
    tokens_per_message = 3
    tokens_per_name = 1
  elif model == "gpt-3.5-turbo-0301":
    tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
    tokens_per_name = -1  # if there's a name, the role is omitted
  elif "gpt-3.5-turbo" in model:
    print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
    return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
  elif "gpt-4" in model:
    print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
    return num_tokens_from_messages(messages, model="gpt-4-0613")
  else:
    raise NotImplementedError(
      f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
    )

  num_tokens = 0
  for message in messages:
    num_tokens += tokens_per_message
    for key, value in message.items():
      num_tokens += len(encoding.encode(value))
      if key == "name":
        num_tokens += tokens_per_name
  
  num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>

  return num_tokens


@cache.memoize()
def generate_docstring_with_openai(
  definition: str,
  definition_type: str,
) -> str:
  assert isinstance(definition, str), "Expected definition to be a string"
  assert isinstance(definition_type, str), "Expected definition_type to be a string"
  assert definition_type in ["function", "class"], "Expected definition_type to be either 'function' or 'class'"

  # Format message for OpenAI API
  messages = [
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
  ]

  # Count number of tokens in message
  num_tokens = num_tokens_from_messages(messages, model=DEFAULT_OPENAI_MODEL_TO_USE)

  # Check if number of tokens is within OpenAI API limits
  if num_tokens <= 4_096:
    model = "gpt-3.5-turbo-0613"
  elif num_tokens <= 16_384:
    model = "gpt-3.5-turbo-16k-0613"
  else:
    logging.warn(col.red(f"Too many tokens ({num_tokens}) for OpenAI API"))

    raise AIDocsEngineTooManyTokensError(
      num_tokens=num_tokens,
    )

  # Log some info
  logging.info(f"Using OpenAI API model {model} for {definition_type} with {num_tokens} tokens")

  # Generate docstring with OpenAI API
  response = openai.ChatCompletion.create(
    model=model,
    messages=messages,
  )

  docstring = response["choices"][0]["message"]["content"]

  return docstring
