from typing import List
from pydantic import BaseModel, Field

from ai_docs_engine.utilities import ConstBaseModel


class FunctionParameterData(ConstBaseModel):
  name:           str = Field(default="", description="The name of the parameter")
  description:    str = Field(default="", description="The description of the parameter")
  assumed_type:   str = Field(default="", description="The assumed type(s) of the parameter; example: 'str, int, float'")


class FunctionReturnData(ConstBaseModel):
  name:           str = Field(default="", description="The name of the return value")
  description:    str = Field(default="", description="The description of the return value")
  assumed_type:   str = Field(default="", description="The assumed type(s) of the return value; example: 'str, int, float'")


class FunctionExceptionData(ConstBaseModel):
  name:           str = Field(default="", description="The name of the exception")
  description:    str = Field(default="", description="The description of the exception")


class FunctionDocstringData(BaseModel):
  description:    str                         = Field(default="", description="The overall description of the function in 1 sentence; this should begin with a verb.")
  parameters:     List[FunctionParameterData] = Field(default=[], description="An array of descriptions for each of the function's parameters, if it has any.")
  return_values:  List[FunctionReturnData]    = Field(default=[], description="An array of descriptions for each of the function's return values, if it has any.")
  exceptions:     List[FunctionExceptionData] = Field(default=[], description="An array of descriptions for each of the exceptions the function may raise, if it has any.")


class ClassDocstringData(BaseModel):
  description:    str = Field(default="", description="The overall description of the class in 1 sentence; this should begin with a verb.")
