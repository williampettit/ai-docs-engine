import json
from pydantic import Field
import diskcache
import logging
import openai

from .docstring_formatter import ClassDocstringData, FunctionDocstringData
from .agent_functions import RESPOND_WITH_STRUCTURED_DOCSTRING_DATA_FOR_CLASS, RESPOND_WITH_STRUCTURED_DOCSTRING_DATA_FOR_FUNCTION
from .meta import SUPPORTED_LANGUAGES
from .utilities import ConstBaseModel, time_func, col
from .errors import AIDocsEngineError


# Cache all OpenAI API calls to avoid paying for same call more than once
cache = diskcache.Cache("data/cache/openai_calls-v2")


class OpenAIModel(ConstBaseModel):
  name:    str = Field(description="The name of the OpenAI model to use")
  tok_lim: int = Field(description="The token limit for the OpenAI model")


# TODO: Allow this to be configured via CLI
DEFAULT_MODEL = OpenAIModel(name="gpt-3.5-turbo-0613", tok_lim=4_096)
EXTRA_CONTEXT_MODEL = OpenAIModel(name="gpt-3.5-turbo-16k-0613", tok_lim=16_384)


@cache.memoize("generate_docstring-v3")
def generate_docstring(
  language: str,
  definition: str,
  definition_type: str,
  temperature: float,
) -> FunctionDocstringData | ClassDocstringData:
  """Generates a docstring for a given class or function definition using OpenAI's API."""

  # Get preferred name stylization for language
  language_name = SUPPORTED_LANGUAGES[language].stylized_name

  # Format messages
  messages = [
    {
      "role": "system",
      "content": f"""You are a robot who is an expert at writing docstrings for {language_name} classes and functions, mainly because you are extremely good at being concise.
Help the human write a docstring for the following {definition_type}:""",
    },
    {
      "role": "user",
      "content": definition,
    },
  ]

  # TODO: select model here based on number of tokens; not yet clear what best way to measure function call tokens is
  # NOTE: an exception will be raised if the model's token limit is exceeded
  model = DEFAULT_MODEL.name # EXTRA_CONTEXT_MODEL.name

  # Pick agent function to use
  if definition_type == "function":
    agent_function = RESPOND_WITH_STRUCTURED_DOCSTRING_DATA_FOR_FUNCTION
  elif definition_type == "class":
    agent_function = RESPOND_WITH_STRUCTURED_DOCSTRING_DATA_FOR_CLASS
  else:
    raise AIDocsEngineError(f"Unsupported definition type: {definition_type}")

  # Log API call
  logging.info(f"Using OpenAI API model {col(model, 'yellow')} @ {col(temperature, 'red')} temperature for a {col(language_name, 'green')} {col(definition_type, 'magenta')}")

  # Generate docstring with OpenAI API
  response = openai.ChatCompletion.create(
    model=model,
    messages=messages,
    temperature=temperature,
    function_call={"name": agent_function["name"],},
    functions=[agent_function,],
  )

  #
  # Extract docstring from response
  #

  # Extract message
  message = response["choices"][0]["message"]

  # If the message is a function call, then the model has failed to generate the docstring
  if "function_call" not in message:
    logging.error(f"Received unexpected message: {message}")
    raise AIDocsEngineError(f"Model {model} failed to generate docstring (message did not include a `function_call`, but instead was: `{message}`)")
  
  # Extract function call
  function_call = message["function_call"]

  # Parse the function call arguments
  if function_call["name"] == "respond_with_structured_docstring_data_for_function":
    # Return the parsed, structured, validated docstring data
    return FunctionDocstringData.parse_obj(
      json.loads(
        function_call["arguments"],
      )
    )
  
  # Parse the function call arguments
  if function_call["name"] == "respond_with_structured_docstring_data_for_class":
    logging.info(f"Received class docstring: {function_call['arguments']}")
    
    # Return the parsed, structured, validated docstring data
    return ClassDocstringData.parse_obj(
      json.loads(
        function_call["arguments"],
      )
    )
  
  # If the function call is not the expected function call, then the model has failed to generate the docstring
  logging.error(f"Received unexpected function call: {function_call}")
  raise AIDocsEngineError(f"Model {model} failed to generate docstring (received unexpceted `function_call` name in response)")
