from typing import Callable, List
from pydantic import Field, validator

from .utilities import ConstBaseModel
from .docstring_formatter import ClassDocstringData, FunctionDocstringData


GenerateDocstringFunc = Callable[
  [
    str,   # language
    str,   # definition
    str,   # definition_type
    float, # temperature
  ],
  FunctionDocstringData | ClassDocstringData, # docstring data
]


class AIDocsEngineConfig(ConstBaseModel):
  """Configuration for AI Docs Engine"""
  include_rules:           List[str] = Field(description="List of glob rules to include files")
  exclude_rules:           List[str] = Field(description="List of glob rules to exclude files")
  inplace:                 bool      = Field(description="Whether to modify files in-place or not", default=False)
  indent_size:             int       = Field(description="Number of spaces to use for indentation", default=2)
  max_workers:             int       = Field(description="Number of workers to use for parallelization", default=10)
  quote_style:             str       = Field(description="Preferred docstring quote style", default='"""')
  temperature:             float     = Field(description="Temperature to use for OpenAI API", default=0.25)
  skip_init_methods:       bool      = Field(description="Whether to skip __init__ methods or not", default=True)
  skip_if_too_many_tokens: bool      = Field(description="Whether to skip definitions if too many tokens or not", default=True)
  generate_docstring_func: GenerateDocstringFunc = Field(description="Function to generate docstrings")
  

  @validator("quote_style")
  def validate_quote_style(cls, value: str) -> str:
    allowed_styles = {'"""', "'''", '"', "'"}
    if value not in allowed_styles:
      raise ValueError(
        f"Invalid docstring quote style: {value}\n"
        f"Allowed styles: {', '.join(allowed_styles)}"
      )
    return value
