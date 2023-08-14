from typing import Set
from pydantic import Field

from ai_docs_engine.utilities import ConstBaseModel


class SupportedLanguage(ConstBaseModel):
  stylized_name: str                   = Field(description="The preferred stylization of this language's name, and the version that is passed to the LLM, e.g. 'C++' instead of 'cpp'")
  supported_definition_types: Set[str] = Field(description="The definition types that are supported for this language, e.g. 'class', 'function', etc.")


SUPPORTED_LANGUAGES = {
  "python": SupportedLanguage(
    stylized_name="Python",
    supported_definition_types={"class", "function",},
  ),

  # TODO: Uncomment these once they're actually supported, still need to find good CST parsers for each
  # "cpp": ...
  # "java": ...
  # "javascript": ...
  # "typescript": ...
}
