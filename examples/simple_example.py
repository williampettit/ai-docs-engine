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
# Properly handles one-line functions now
def dot(a, b): return sum([an * bn for (an, bn) in zip(a, b)])
    """
  )

# Define config
config = ai_docs_engine.AIDocsEngineConfig(
  # Use inplace mode for this example
  inplace=True,
  
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
