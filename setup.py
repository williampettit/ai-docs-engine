from setuptools import setup, find_packages


with open("README.md") as file:
  long_description = file.read()


setup(
  # basic info
  name="ai-docs-engine",
  version="0.1.0",
  author="William Pettit",
  license="MIT",
  description="`Experimental AI docstring tool",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/williampettit/ai-docs-engine",
  project_urls={
    "Source Code": "https://github.com/williampettit/ai-docs-engine",
  },
  packages=find_packages(),
  package_dir={
    "ai_docs_engine": "ai_docs_engine",
  },

  # requirements
  python_requires=">=3.6",
  install_requires=[
    "libcst",
    "openai",
    "pydantic",
  ],

  # testing
  test_suite="tests",
  tests_require=[
    "pytest",
  ],
)
