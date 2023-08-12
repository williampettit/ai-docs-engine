import logging
logging.getLogger("openai").setLevel("ERROR")
logging.getLogger("urllib3").setLevel("ERROR")

import dotenv
dotenv.load_dotenv()

from glob import glob
from libcst.metadata import MetadataWrapper
from pydantic import BaseModel
from typing import List
import libcst
import os
from concurrent.futures import ThreadPoolExecutor

from .docstring_transformer import DocstringTransformer
from .openai_calls import generate_docstring_with_openai
from .utilities import time_func


class Config(BaseModel):
  include_rules: List[str]
  exclude_rules: List[str]
  modify_files_inplace: bool
  docstring_quote_style: str = '"""'
  skip_init_functions: bool
  skip_definition_if_too_many_tokens: bool

  # ... 
  _max_workers: int = 10


@time_func
def gather_source_file_paths(
  include_rules: List[str],
  exclude_rules: List[str],
) -> list[str]:
  assert isinstance(include_rules, List), "Expected include_rules to be a list"
  assert isinstance(exclude_rules, List), "Expected exclude_rules to be a list"
  
  include_paths = []
  exclude_paths = []

  # Gather all source files to include
  for path in include_rules:
    assert isinstance(path, str), "Expected path in include_rules to be a string"
    paths = glob(path)
    include_paths.extend(paths)

  # Gather all source files to exclude
  for path in exclude_rules:
    assert isinstance(path, str), "Expected path in exclude_rules to be a string"
    paths = glob(path)
    exclude_paths.extend(paths)

  # Remove all excluded paths from the included paths
  paths = set(include_paths) - set(exclude_paths)

  # Check that there is at least one path
  if len(paths) == 0:
    raise Exception("No paths to process")

  # Return the set as a sorted list
  return sorted(list(paths))


def generate_docstrings_for_file(
  config: Config,
  source_file_path: str,
):
  # Load source code
  with open(source_file_path) as file:
    source = file.read()

  # Parse source code and wrap module in metadata wrapper
  wrapper = MetadataWrapper(libcst.parse_module(source))

  # Extract module from wrapper
  module = wrapper.module

  # Initialize docstring transformer and supply OpenAI wrapper function
  transformer = DocstringTransformer(
    module=module,
    docstring_quote_style=config.docstring_quote_style,
    generate_docstring_func=generate_docstring_with_openai,
    skip_init_functions=config.skip_init_functions,
    skip_definition_if_too_many_tokens=config.skip_definition_if_too_many_tokens,
  )

  # Resolve metadata
  transformer.resolve(wrapper)

  # Apply docstring transformer to source code
  modified_module = wrapper.visit(transformer)

  # Write transformed code to file
  if config.modify_files_inplace:
    with open(source_file_path, "w") as file:
      file.write(modified_module.code)
  else:
    source_file_dir = os.path.dirname(source_file_path)
    
    modified_source_file_path = os.path.join(source_file_dir, f"modified_{os.path.basename(source_file_path)}")
    
    # if os.path.exists(modified_source_file_path):
    #   raise Exception(f"File already exists: {modified_source_file_path}")

    with open(modified_source_file_path, "w") as file:
      file.write(modified_module.code)


@time_func
def generate_docstrings(
  config: Config
) -> None:
  # Gather all source file paths to be processed
  source_file_paths = gather_source_file_paths(
    include_rules=config.include_rules,
    exclude_rules=config.exclude_rules,
  )

  # Count total source files
  total_source_files = len(source_file_paths)

  # Process each source file
  with ThreadPoolExecutor(max_workers=config._max_workers) as executor:
    for (index, source_file_path) in enumerate(source_file_paths):
      # Print progress
      logging.info(f"[{index + 1}/{total_source_files}] Processing source file `{source_file_path}`")

      # Generate docstrings for file
      executor.submit(generate_docstrings_for_file, config, source_file_path)