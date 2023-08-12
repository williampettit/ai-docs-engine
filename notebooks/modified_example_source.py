##
## This file contains dummy source code for the notebook to use.
## It is used to test the parser.
##


async def example_func_0():
  """Prints "Hello"."""
  print("Hello")


def example_func_1(arg0, arg1):
  """Prints the values of `arg0` and `arg1` to the console."""
  # Pre-existing comment, which should not be considered as a docstring
  print(arg0, arg1)


def example_func_2():
  """Pre-existing docstring, which should never be overwritten."""
  return 42


class Calculator:
  def __init__(self, value) -> None:
    """Assigns the given value to the "value" attribute of the object."""
    self.value = value
  
  def add(self, value):
    """Increments the value attribute of an object by a given value."""
    self.value += value

  def subtract(self, value):
    """Subtracts the given value from the attribute value of the object."""
    self.value -= value
  