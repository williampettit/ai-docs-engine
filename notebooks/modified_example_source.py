##
## This file contains dummy source code for the notebook to use.
## It is used to test the parser.
##

def example_func_0():
  """Placeholder docstring."""
  print("Hello")

def example_func_1(arg0, arg1):
  """Placeholder docstring."""
  # Pre-existing comment, but not docstring
  print(arg0, arg1)

def example_func_2():
  """Pre-existing docstring"""
  return 42

class ExampleClass:
  def __init__(self, value) -> None:
    """Placeholder docstring."""
    self.value = value

  def print(self):
    """Pre-existing docstring"""
    print(self.value)

  def print_reversed(self):
    """Placeholder docstring."""
    print(reversed(self.value))
