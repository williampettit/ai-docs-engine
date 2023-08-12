import os

import ai_docs_engine


def test_simple():
  # Remove output from previous tests
  previous_test_output = "tests/data/modified_example_source.py"
  if os.path.exists(previous_test_output):
    os.remove(previous_test_output)
  
  # Define config
  config = ai_docs_engine.Config(
    include_rules=["tests/data/**.py"],
    exclude_rules=[],
    modify_files_inplace=False,
    skip_init_functions=True,
    docstring_quote_style='"""',
  )

  # Generate docstrings
  ai_docs_engine.generate_docstrings(config)
