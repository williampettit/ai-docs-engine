from pydantic import BaseModel
from typing import Any
import time

from ai_docs_engine.logger import logger, col


class ConstBaseModel(BaseModel):
  def __setattr__(self, name, value):
    if name in self.__dict__:
      raise ValueError(f"Field '{name}' is const and cannot be modified.")
    super().__setattr__(name, value)


def time_func(func):
  """Basic timer decorator"""

  def wrapper(*args, **kwargs) -> Any:
    start_time = time.perf_counter()
    func_return_value = func(*args, **kwargs)
    time_taken = time.perf_counter() - start_time

    func_name = col(f"{func.__name__}", "magenta")
    time_taken = col(f"{time_taken:.2f}", "green")
    logger.info(f"Time taken to execute {func_name}: {time_taken} seconds")

    return func_return_value

  return wrapper


def capitalize_first_letter(string: str) -> str:
  assert isinstance(string, str), "Expected string to be a string"

  # Trim leading and trailing whitespace
  string = string.strip()
  assert len(string) > 0, "Expected string to be non-empty"

  # Capitalize first letter
  return string[0].upper() + string[1:]
