from typing import Callable, List
from pydantic import Field, validator

from ai_docs_engine.utilities import ConstBaseModel
from ai_docs_engine.docstring_schema import ClassDocstringData, FunctionDocstringData
from ai_docs_engine.docstring_builders import BaseDocstringBuilder, GoogleDocstringBuilder


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
  """Configuration for Pydantic BaseModel"""
  class Config:
    arbitrary_types_allowed = True

  """Configuration for AI Docs Engine"""
  include_rules:           List[str] = Field(description="List of glob rules to include files")
  exclude_rules:           List[str] = Field(description="List of glob rules to exclude files")
  inplace:                 bool      = Field(description="Whether to modify files in-place or not", default=False)
  max_workers:             int       = Field(description="Number of workers to use for parallelization", default=16)
  quote_style:             str       = Field(description="Preferred docstring quote style", default='"""')
  temperature:             float     = Field(description="Temperature to use for OpenAI API", default=0.25)
  skip_init_methods:       bool      = Field(description="Whether to skip __init__ methods or not", default=True)
  generate_docstring_func: GenerateDocstringFunc = Field(description="Function to generate docstrings")
  docstring_builder:       BaseDocstringBuilder  = Field(description="Docstring builder to use", default=GoogleDocstringBuilder())


  @validator("quote_style")
  def validate_quote_style(cls, value: str) -> str:
    allowed_styles = {'"""', "'''", '"', "'"}
    if value not in allowed_styles:
      raise ValueError(
        f"Invalid docstring quote style: {value}\n"
        f"Allowed styles: {', '.join(allowed_styles)}"
      )
    return value


  @validator("docstring_builder")
  def validate_docstring_builder(cls, value: BaseDocstringBuilder) -> BaseDocstringBuilder:
    if not isinstance(value, BaseDocstringBuilder):
      raise ValueError(
        f"Invalid docstring builder: {value}\n"
        f"Must be an instance of {BaseDocstringBuilder}"
      )
    return value
