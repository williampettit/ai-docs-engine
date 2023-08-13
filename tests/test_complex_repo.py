import logging
import subprocess

import ai_docs_engine
import ai_docs_engine.openai_wrapper


def download_repo(repo_url: str, dst_dir: str):
  assert isinstance(repo_url, str), "Expected repo_url to be a string"
  assert isinstance(dst_dir, str), "Expected dst_dir to be a string"

  subprocess.run(["git", "clone", repo_url, dst_dir])

  logging.info("Downloaded repo")


def test_complex_repo():
  # For this example, I will use a sufficiently complex repo, `tinygrad`
  repo_url = "https://github.com/tinygrad/tinygrad"
  dst_dir = "tests/data/repos/tinygrad"

  # Download repo
  download_repo(
    repo_url=repo_url,
    dst_dir=dst_dir,
  )

  # Define config
  config = ai_docs_engine.AIDocsEngineConfig(
    include_rules=[
      "tests/data/repos/tinygrad/tinygrad/**/*.py",
    ],
    exclude_rules=[
      # Ignore files from previous test runs
      "tests/data/repos/tinygrad/tinygrad/**/modified_*.py",
      
      # Ignore `tinygrad` tests
      "tests/data/repos/tinygrad/tinygrad/test_*.py",
    ],
    inplace=False,
    skip_init_methods=True,
    quote_style='"""',
    skip_if_too_many_tokens=True,
    generate_docstring_func=ai_docs_engine.openai_wrapper.generate_docstring,
  )

  # Generate docstrings
  ai_docs_engine.generate_docstrings(config)


if __name__ == "__main__":
  test_complex_repo()
