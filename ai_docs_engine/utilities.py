import logging
import time

try:
  from termcolor import colored as col
except ImportError:
  logging.warning("termcolor is not installed, so colored text will not be available.")

  col = lambda text, *_: text


col # This is here to prevent an unused import warning


class AIDocsEngineError(Exception):
  """
  This is the base class for any Exception that is intentionally raised
  from within the project, that way they can all be caught together.
  """
  pass


class AIDocsEngineTooManyTokensError(AIDocsEngineError):
  def __init__(
    self,
    num_tokens: int,
  ) -> None:
    super().__init__(
      f"There is no OpenAI API model that can handle this many tokens ({num_tokens}), and I have not yet implemented the logic to pre-process the input to fit within the OpenAI API limits."
    )


def time_func(func: callable):
  """
  Timer decorator
  """

  def wrapper(*args, **kwargs):
    start_time = time.perf_counter()
    result = func(*args, **kwargs)
    end_time = time.perf_counter()
    time_taken = end_time - start_time
    
    logging.info(f"Time taken to execute {func.__name__}: {time_taken:.1f} seconds")

    return result

  return wrapper
