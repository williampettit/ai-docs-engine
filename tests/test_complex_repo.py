import logging
import subprocess

import ai_docs_engine


def download_repo(repo_url: str, dst_dir: str):
  assert isinstance(repo_url, str), "Expected repo_url to be a string"
  assert isinstance(dst_dir, str), "Expected dst_dir to be a string"

  logging.info("Downloading repo")
  
  subprocess.run(["git", "clone", repo_url, dst_dir])

  logging.info("Downloaded repo")


def test_complex_repo():
  logging.info("Running test_complex_repo")

  # For this example, I will use a sufficiently complex repo, `tinygrad`
  repo_url = "https://github.com/tinygrad/tinygrad"
  dst_dir = "tests/test_data/repos/tinygrad"

  # Download repo
  download_repo(
    repo_url=repo_url,
    dst_dir=dst_dir,
  )

  # Define config
  config = ai_docs_engine.Config(
    include_rules=[
      "tests/test_data/repos/tinygrad/tinygrad/**/*.py",

      # TEMP: Test specific path so that the test runs faster
      # "tests/test_data/repos/tinygrad/tinygrad/test_add.py",
    ],
    exclude_rules=[
      # Ignore files from previous test runs
      "tests/test_data/repos/tinygrad/tinygrad/**/modified_*.py",
      
      # Ignore `tinygrad` tests
      "tests/test_data/repos/tinygrad/tinygrad/test_*.py",
    ],
    modify_files_inplace=False,
    skip_init_functions=True,
    docstring_quote_style='"""',
    skip_definition_if_too_many_tokens=True,
  )

  # Generate docstrings
  ai_docs_engine.generate_docstrings(config)


if __name__ == "__main__":
  test_complex_repo()
