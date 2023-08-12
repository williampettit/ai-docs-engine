import subprocess

import ai_docs_engine


def download_repo(repo_url: str, dst_dir: str):
  assert isinstance(repo_url, str), "Expected repo_url to be a string"
  assert isinstance(dst_dir, str), "Expected dst_dir to be a string"

  # Download repo
  subprocess.run(["git", "clone", repo_url, dst_dir])


def test_complex_repo():
  # For this example, I will use the sufficiently complex repo, `tinygrad`
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
      "tests/test_data/repos/tinygrad/tinygrad/**.py",
    ],
    exclude_rules=[
      "tests/test_data/repos/tinygrad/tinygrad/test_*.py",
    ],
    modify_files_inplace=False,
    skip_init_functions=True,
    docstring_quote_style='"""',
  )

  # Generate docstrings
  ai_docs_engine.generate_docstrings(config)
