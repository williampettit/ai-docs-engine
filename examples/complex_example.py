##
## The complex example is a more realistic example of how the tool can be used. 
## I will download a sufficiently complex repo from GitHub and generate docstrings for it here. 
##

import os
import subprocess

import ai_docs_engine
import ai_docs_engine.openai_docstring_agent
import ai_docs_engine.docstring_builders


# Define paths
repo_url = "https://github.com/tinygrad/tinygrad"
repo_dst_dir = "data/repos/tinygrad"

# Remove repo if it already exists
if os.path.exists(repo_dst_dir):
  subprocess.run(["rm", "-rf", repo_dst_dir])

# Clone fresh copy of repo
subprocess.run(["git", "clone", repo_url, repo_dst_dir])

# Define config
config = ai_docs_engine.AIDocsEngineConfig(
  include_rules=[
    # Include all Python files in `tinygrad` folder in repo
    # f"{repo_dst_dir}/tinygrad/**/*.py",

    # Test on single file
    f"{repo_dst_dir}/tinygrad/runtime/ops_cpu.py",
  ],
  exclude_rules=[
    # Ignore files from previous usage
    f"{repo_dst_dir}/tinygrad/**/modified_*.py",
    # Ignore `tinygrad` tests
    f"{repo_dst_dir}/**/test_*.py",
  ],

  # Specify function to generate docstrings
  generate_docstring_func=ai_docs_engine.openai_docstring_agent.generate_docstring,

  # Specify docstring builder
  docstring_builder=ai_docs_engine.docstring_builders.NumpyDocstringBuilder(),
)

# Generate docstrings
processed_source_files = ai_docs_engine.generate_docstrings(config)

# Check that output files were created and are not empty
for (root, dirs, files) in os.walk(repo_dst_dir):
  for file in files:
    if file in processed_source_files:
      modified_file_path = processed_source_files[file]
      assert os.path.exists(modified_file_path), f"Expected {modified_file_path} to exist"
      assert os.path.getsize(modified_file_path) > 0, f"Expected {modified_file_path} to be non-empty"
