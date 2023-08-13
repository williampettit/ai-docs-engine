import os
import pytest

import ai_docs_engine
import ai_docs_engine.openai_wrapper


def test_simple():
  # Remove output from previous tests
  previous_test_output = "tests/data/modified_example_source.py"
  if os.path.exists(previous_test_output):
    os.remove(previous_test_output)
  
  # Define config
  config = ai_docs_engine.AIDocsEngineConfig(
    include_rules=["tests/data/**.py"],
    exclude_rules=["tests/data/modified_**.py"],
    inplace=False,
    skip_init_methods=True,
    quote_style='"""',
    max_workers=10,
    skip_if_too_many_tokens=True,
    generate_docstring_func=ai_docs_engine.openai_wrapper.generate_docstring,
  )

  # Generate docstrings
  ai_docs_engine.generate_docstrings(config=config)

  # Check that output file was created
  assert os.path.exists(previous_test_output)