##
## This file contains dummy source code for the notebook to use.
## It is used to test the parser.
##


async def download_repo(
  repo_url: str,
  dst_dir: str,
  print_progress: bool = True,
) -> None:
  await download(repo_url, dst_dir, print_progress=print_progress)


async def example_func_0():
  print("Hello")


def example_func_1(arg0, arg1):
  # Pre-existing comment, which should not be considered as a docstring
  print(arg0, arg1)


def example_func_2():
  """Pre-existing docstring, which should never be overwritten."""
  return 42


class Calculator:
  def __init__(self, value) -> None:
    self.value = value
  
  def add(self, value):
    self.value += value

  def subtract(self, value):
    self.value -= value
  