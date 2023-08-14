import dotenv
dotenv.load_dotenv()

import concurrent.futures
from glob import glob
from libcst.metadata import MetadataWrapper
from typing import Dict, List
import libcst
import os

from ai_docs_engine.python_docstring_inserter import PythonDocstringInserter
from ai_docs_engine.errors import AIDocsEngineError
from ai_docs_engine.config import AIDocsEngineConfig
from ai_docs_engine.logger import logger


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
) -> str:
  # Log start of docstring generation for current file
  logger.info(f"Generating docstrings for file `{file_path}`")
  
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
  transformer = PythonDocstringInserter(
    module=module,
    config=config,
  )

  # Resolve metadata
  transformer.resolve(wrapper)

  # Apply docstring transformer to source code
  modified_module = wrapper.visit(transformer)

  # Determine path to write to based on whether or not the user wants to overwrite the original file
  if config.inplace:
    path_to_write_to = file_path
  else:
    file_dir = os.path.dirname(file_path)
    path_to_write_to = os.path.join(file_dir, f"modified_{os.path.basename(file_path)}")

  # Write transformed code to file
  with open(path_to_write_to, "w") as file:
    file.write(modified_module.code)

  # Return the original file path and the path that the modified code was written to
  return (file_path, path_to_write_to)


def generate_docstrings(
  config: AIDocsEngineConfig,
) -> Dict[str, str]:
  # Gather all source file paths to be processed
  source_file_paths = _gather_source_file_paths(
    include_rules=config.include_rules,
    exclude_rules=config.exclude_rules,
  )

  # Count total source files
  total_source_files = len(source_file_paths)

  # Log number of source files to be processed
  logger.info(f"Found {total_source_files} source files to process")

  # Store processed source files in a dictionary which maps their original paths to their modified paths
  processed_source_files = {}

  # Process source files in parallel
  with concurrent.futures.ThreadPoolExecutor(max_workers=config.max_workers) as executor:
    # Submit all source files to executor
    futures = [
      executor.submit(
        _generate_docstrings_for_file,
        config=config,
        file_path=source_file_path,
      )
      for source_file_path in source_file_paths
    ]
    
    # Process futures as they complete
    for future in concurrent.futures.as_completed(futures):
      try:
        # Add result to dictionary of processed source files
        (original_path, modified_path) = future.result()
        processed_source_files[original_path] = modified_path

      except Exception as exception:
        logger.error(f"Error while processing a source file. ({exception = })")

  # Log end of docstring generation
  logger.info("Docstring generation complete")

  # Return processed source files as a dictionary which maps their original paths to their modified paths
  return processed_source_files
