from pydantic import Field
import diskcache
import openai
import json

from ai_docs_engine.agent_functions import RESPOND_WITH_STRUCTURED_DOCSTRING_DATA_FOR_CLASS, RESPOND_WITH_STRUCTURED_DOCSTRING_DATA_FOR_FUNCTION
from ai_docs_engine.docstring_schema import ClassDocstringData, FunctionDocstringData
from ai_docs_engine.errors import AIDocsEngineError, AIDocsEngineTooManyTokensError
from ai_docs_engine.meta import SUPPORTED_LANGUAGES
from ai_docs_engine.utilities import ConstBaseModel, time_func
from ai_docs_engine.logger import logger, col


# Cache all OpenAI API calls to avoid paying for same call more than once
cache = diskcache.Cache("data/cache/openai")


class OpenAIModel(ConstBaseModel):
  name:    str = Field(description="The name of the OpenAI model to use")
  tok_lim: int = Field(description="The token limit for the OpenAI model")


# TODO: Allow these to be configured via CLI, should dynamically fetch latest token limit for each model as well
DEFAULT_MODEL = OpenAIModel(name="gpt-3.5-turbo-0613", tok_lim=4_096)
EXTRA_CONTEXT_MODEL = OpenAIModel(name="gpt-3.5-turbo-16k-0613", tok_lim=16_384)


@cache.memoize()
def generate_docstring(
  language: str,
  definition: str,
  definition_type: str,
  temperature: float,
) -> FunctionDocstringData | ClassDocstringData:
  """
  Generates a docstring for a given class or function definition using OpenAI's API.
  
  Args:
    language: The programming language of the input definition
    definition: The definition to generate a docstring for (e.g. "def foo(): ..." or "class Foo: ...")
    definition_type: The type of definition (e.g. "function", "class")
    temperature: The temperature to use for the OpenAI API

  Returns:
    The parsed, structured, and validated docstring data
  """

  # Define agent function map
  agent_function_map = {
    "function": {
      "agent_function": RESPOND_WITH_STRUCTURED_DOCSTRING_DATA_FOR_FUNCTION,
      "response_type":  FunctionDocstringData,
    },
    "class": {
      "agent_function": RESPOND_WITH_STRUCTURED_DOCSTRING_DATA_FOR_CLASS,
      "response_type":  ClassDocstringData,
    },
  }

  # Validate definition type
  assert definition_type in agent_function_map, f"Unsupported definition type: {definition_type}"

  # Get preferred name stylization for language
  language_name = SUPPORTED_LANGUAGES[language].stylized_name

  # Build system prompt
  system_prompt = "\n".join([
    f"You are a robot who is an expert at writing docstrings for {language_name} classes and functions, mainly because you are extremely good at being concise.",
    f"Help the human write a docstring for the following {definition_type}:",
  ])

  # Format messages
  messages = [
    { "role": "system", "content": system_prompt, },
    { "role": "user", "content": definition, },
  ]

  # TODO: count total tokens in `messages`
  # ...

  # TODO: select model here based on number of tokens; not yet clear what best way to measure function call tokens is
  model = DEFAULT_MODEL.name # EXTRA_CONTEXT_MODEL.name
  
  # Select agent function to use
  agent_function = agent_function_map[definition_type]["agent_function"]
  
  # Log API call
  logger.info(
    f"Using OpenAI API model `{col(model, 'yellow')}` for a {col(language_name, 'green')} {col(definition_type, 'magenta')} ({col(definition[:20], 'cyan')})"
  )

  # Generate docstring with OpenAI API
  # NOTE: an exception will be raised if the model's token limit is exceeded
  try:
    response = openai.ChatCompletion.create(
      model=model,
      messages=messages,
      temperature=temperature,
      functions=[
        agent_function,
      ],
      function_call={
        "name": agent_function["name"],
      },
    )

  # If the token limit was exceeded, then raise a custom error
  except openai.InvalidRequestError as exception:
    if exception.code == "context_length_exceeded":
      raise AIDocsEngineTooManyTokensError() from exception
    
    # Otherwise, raise the original exception
    raise exception

  # If the message is not a function call, then the model failed to generate the docstring
  message = response["choices"][0]["message"]
  if "function_call" not in message:
    logger.error(f"Received unexpected message: {message}")
    raise AIDocsEngineError(f"Model {model} failed to generate docstring (message did not include a `function_call`, but instead was: `{message}`)")
  
  # Extract function call
  function_call = message["function_call"]

  # If the function call is not one of the expected function calls, then the model has failed to generate the docstring
  assert function_call["name"] == agent_function["name"], f"Unexpected function call name received: {function_call['name']}"

  # Get the type of the structured docstring data to return
  response_type = agent_function_map[definition_type]["response_type"]

  # Return the parsed, structured, validated docstring data
  try:
    return response_type.parse_raw(function_call["arguments"])
  except Exception as exception:
    note = (
      "Failed to parse OpenAI response.\n"
      f"{response = }\n"
      f"{definition = }\n"
      f"{definition_type = }"
    )
    logger.error(note)
    exception.add_note(note)
    raise exception
