# This file contains the agent functions that are used by the AI Docs Engine.

from .docstring_formatter import ClassDocstringData, FunctionDocstringData


# TODO: Add more agent functions here

# This agent function generates the structured data for a function docstring.
RESPOND_WITH_STRUCTURED_DOCSTRING_DATA_FOR_FUNCTION = {
  "name": "respond_with_structured_docstring_data_for_function",
  "parameters": FunctionDocstringData.schema(),
}

# This agent function generates the structured data for a class docstring.
RESPOND_WITH_STRUCTURED_DOCSTRING_DATA_FOR_CLASS = {
  "name": "respond_with_structured_docstring_data_for_class",
  "parameters": ClassDocstringData.schema(),
}