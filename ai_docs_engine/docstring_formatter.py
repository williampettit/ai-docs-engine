from typing import List
from pydantic import BaseModel, Field

from .utilities import ConstBaseModel


class FunctionParameterData(ConstBaseModel):
  name:         str = Field(description="The name of the parameter")
  description:  str = Field(description="The description of the parameter")
  assumed_type: str = Field(description="The assumed type(s) of the parameter; example: 'str, int, float'")


class FunctionReturnData(ConstBaseModel):
  name:         str = Field(description="The name of the return value")
  description:  str = Field(description="The description of the return value")
  assumed_type: str = Field(description="The assumed type(s) of the return value; example: 'str, int, float'")


class FunctionExceptionData(ConstBaseModel):
  name:        str = Field(description="The name of the exception")
  description: str = Field(description="The description of the exception")


class FunctionDocstringData(BaseModel):
  description:   str                         = Field(description="The overall description of the function in 1 sentence; this should begin with a verb.")
  parameters:    List[FunctionParameterData] = Field(description="An array of descriptions for each of the function's parameters, if it has any.")
  return_values: List[FunctionReturnData]    = Field(description="An array of descriptions for each of the function's return values, if it has any.")
  exceptions:    List[FunctionExceptionData] = Field(description="An array of descriptions for each of the exceptions the function may raise, if it has any.")


class ClassDocstringData(BaseModel):
  description: str = Field(description="The overall description of the class in 1 sentence; this should begin with a verb.")


def build_numpy_docstring(
  data: FunctionDocstringData | ClassDocstringData,
  overall_indent: int,
  section_body_indent: int,
) -> str:
  lines = []
  indent = " " * overall_indent
  body_indent = " " * section_body_indent

  # Description
  lines.append(f"{data.description}")

  # Add function exclusive sections
  if isinstance(data, FunctionDocstringData):
    # Parameters
    if data.parameters:
      lines.append("")
      lines.append("Parameters")
      lines.append("----------")
      for param in data.parameters:
        lines.append(f"{body_indent}{param.name} : {param.assumed_type}")
        lines.append(f"{body_indent}{body_indent}{param.description}")

    # Return Values
    if data.return_values:
      lines.append("")
      lines.append("Returns")
      lines.append("-------")
      for ret in data.return_values:
        lines.append(f"{body_indent}{ret.name} : {ret.assumed_type}")
        lines.append(f"{body_indent}{body_indent}{ret.description}")

    # Exceptions
    if data.exceptions:
      lines.append("")
      lines.append("Raises")
      lines.append("------")
      for exc in data.exceptions:
        lines.append(f"{body_indent}{exc.name}")
        lines.append(f"{body_indent}{body_indent}{exc.description}")
  
  # Indent the lines
  if len(lines) > 1:
    lines.insert(0, "")
    lines.append("")
    lines = [ indent + line for line in lines ]

  return "\n".join(lines)


def build_google_docstring():
   raise NotImplementedError("build_google_docstring() is not yet implemented.")
