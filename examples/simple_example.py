import os

import ai_docs_engine
import ai_docs_engine.openai_docstring_agent
import ai_docs_engine.docstring_builders


# Define paths
original_code_path = "data/simple_source_code_demo.py"
modified_code_path = "data/modified_simple_source_code_demo.py"

# Write example code to file
with open(original_code_path, "w") as file:
  file.write(
    """
def one(x, y): x += 5; y += 2.5; return x // y * math.pi

################################
################################

def foo(a, b, c):
  def buzz(x, y): return (x + y)  // 3
  
  def bar(a, b):
    return a + b
  
  return (a + b) * c
    """
  )

# Define config
config = ai_docs_engine.AIDocsEngineConfig(
  # Files to include
  include_rules=[
    original_code_path,
  ],

  # Files to exclude
  exclude_rules=[
    # Ignore files from previous test runs
    modified_code_path,
  ],

  # Specify function to generate docstrings
  generate_docstring_func=ai_docs_engine.openai_docstring_agent.generate_docstring,

  # Specify docstring builder
  docstring_builder=ai_docs_engine.docstring_builders.GoogleDocstringBuilder(),
)

# Generate docstrings
ai_docs_engine.generate_docstrings(config)

# Check that output file was created
assert os.path.exists(modified_code_path)

# Check that output file is not empty
assert os.path.getsize(modified_code_path) > 0

# Check that output file is not the same as input file
with open(modified_code_path, "r") as file:
  output_code = file.read()
with open(original_code_path, "r") as file:
  input_code = file.read()
assert output_code != input_code

# Print output code
print(output_code)
