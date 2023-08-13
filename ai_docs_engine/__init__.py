import logging
logging.getLogger("openai").setLevel("ERROR")
logging.getLogger("urllib3").setLevel("ERROR")

import dotenv
dotenv.load_dotenv()

from concurrent.futures import ThreadPoolExecutor
from glob import glob
from libcst.metadata import MetadataWrapper
from typing import List
import libcst
import os

from .docstring_transformer import DocstringTransformer
from .errors import AIDocsEngineError
from .config import AIDocsEngineConfig


def _gather_source_file_paths(
  include_rules: List[str],
  exclude_rules: List[str],
) -> List[str]:
  assert isinstance(include_rules, List), "Expected include_rules to be a list"
  assert isinstance(exclude_rules, List), "Expected exclude_rules to be a list"
  
  include_paths = []
  exclude_paths = []

  # Gather all source files to include
  for rule in include_rules:
    assert isinstance(rule, str), "Expected rule in include_rules to be a string"
    paths = glob(rule)
    include_paths.extend(paths)

  # Gather all source files to exclude
  for rule in exclude_rules:
    assert isinstance(rule, str), "Expected rule in exclude_rules to be a string"
    paths = glob(rule)
    exclude_paths.extend(paths)

  # Remove all excluded paths from the included paths
  paths = set(include_paths) - set(exclude_paths)

  # Check that there is at least one path
  if len(paths) == 0:
    raise AIDocsEngineError("No paths to process")

  # Return the set as a sorted list
  return sorted(list(paths))


def _generate_docstrings_for_file(
  config: AIDocsEngineConfig,
  file_path: str,
) -> None:
  # Read source code from file
  with open(file_path) as file:
    code = file.read()

  # Parse source code into module
  module = libcst.parse_module(code)

  # Wrap module in metadata wrapper; makes a deep copy of the module
  wrapper = MetadataWrapper(module)

  # Extract deep copied module from wrapper
  module = wrapper.module

  # Initialize docstring transformer and supply OpenAI wrapper function
  transformer = DocstringTransformer(
    module=module,
    config=config,
  )

  # Resolve metadata
  transformer.resolve(wrapper)

  # Apply docstring transformer to source code
  modified_module = wrapper.visit(transformer)

  # Write transformed code to file
  if config.inplace:
    # Overwrite original file
    with open(file_path, "w") as file:
      file.write(modified_module.code)
  
  else:
    # Write modified code to new file
    file_dir = os.path.dirname(file_path)
    modified_file_path = os.path.join(file_dir, f"modified_{os.path.basename(file_path)}")
    with open(modified_file_path, "w") as file:
      file.write(modified_module.code)


def generate_docstrings(
  config: AIDocsEngineConfig,
) -> None:
  # Gather all source file paths to be processed
  source_file_paths = _gather_source_file_paths(
    include_rules=config.include_rules,
    exclude_rules=config.exclude_rules,
  )

  # Count total source files
  total_source_files = len(source_file_paths)

  # Process each source file
  with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
    for (index, source_file_path) in enumerate(source_file_paths):
      # Log progress
      logging.info(f"[{index + 1}/{total_source_files}] Processing source file `{source_file_path}`")
      
      # Generate docstrings for current file
      executor.submit(
        _generate_docstrings_for_file,
        config=config,
        file_path=source_file_path,
      )
