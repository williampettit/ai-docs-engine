import logging
from libcst.metadata import PositionProvider
from typing_extensions import override
import libcst

from .docstring_formatter import ClassDocstringData, FunctionDocstringData, build_numpy_docstring
from .utilities import capitalize_first_letter, time_func
from .config import AIDocsEngineConfig
from .errors import AIDocsEngineError


def preprocess_func_or_class_def(definition: str) -> str:
  assert isinstance(definition, str), "Expected definition to be a string"
  
  # TODO: try to further minimize tokens passed to OpenAI API

  # Remove empty lines
  definition = "\n".join([line for line in definition.splitlines() if line.strip()])

  # Trim leading and trailing whitespace
  definition = definition.strip()

  return definition


def postprocess_docstring(
  docstring_data: FunctionDocstringData | ClassDocstringData,
) -> FunctionDocstringData | ClassDocstringData:
  assert isinstance(docstring_data, (FunctionDocstringData | ClassDocstringData)), "Expected docstring_data to be a function or a class docstring data object"

  PREFIXES_TO_REMOVE = [
    "This function",
    "This method",
    "This class",
  ]

  # Get docstring description
  docstring_desc = docstring_data.description

  # Remove leading prefixes from description
  for prefix in PREFIXES_TO_REMOVE:
    if docstring_desc.startswith(prefix):
      docstring_desc = docstring_desc.removeprefix(prefix)
      break
  
  # Remove leading and trailing whitespace
  docstring_desc = docstring_desc.strip()

  # Capitalize first letter
  docstring_desc = capitalize_first_letter(docstring_desc)

  # TEMP
  docstring_desc = f"AI: {docstring_desc}"

  # Update docstring description with the preprocessed one
  docstring_data.description = docstring_desc

  return docstring_data


def check_if_node_has_docstring(
  node: libcst.FunctionDef | libcst.ClassDef,
) -> bool:
  assert isinstance(node, (libcst.FunctionDef | libcst.ClassDef)), "Expected node to be a function or a class definition"

  # TODO: make this more readable / check if this is the best way to check for docstrings
  first_stmt_line = node.body.body and isinstance(node.body.body[0], libcst.SimpleStatementLine)
  has_expr = first_stmt_line and node.body.body[0].body and isinstance(node.body.body[0].body[0], libcst.Expr)
  has_docstr = has_expr and isinstance(node.body.body[0].body[0].value, libcst.SimpleString)

  return has_docstr


class DocstringTransformer(libcst.CSTTransformer):
  # Declare metadeta dependencies
  METADATA_DEPENDENCIES = (PositionProvider, )


  def __init__(
    self,
    module: libcst.Module,
    config: AIDocsEngineConfig,
  ) -> None:
    assert isinstance(module, libcst.Module), "Expected module to be a `libcst.Module`"
    assert isinstance(config, AIDocsEngineConfig), "Expected config to be an `AIDocsEngineConfig`"

    self._module = module
    self._config = config

    super().__init__()


  def extract_node_source_code(
    self,
    node: libcst.FunctionDef | libcst.ClassDef,
  ) -> str:
      assert isinstance(node, (libcst.FunctionDef | libcst.ClassDef)), "Expected node to be a function or a class definition"
      
      return self._module.code_for_node(node)


  def generate_docstring(
    self,
    node: libcst.FunctionDef | libcst.ClassDef,
  ) -> FunctionDocstringData | ClassDocstringData:
      assert isinstance(node, (libcst.FunctionDef | libcst.ClassDef)), "Expected node to be a function or a class definition"

      # Extract node source code
      node_source_code = self.extract_node_source_code(node)

      # Preprocess function or class definition to minimize tokens passed to OpenAI API
      node_source_code = preprocess_func_or_class_def(node_source_code)

      # Determine node type
      if isinstance(node, libcst.FunctionDef):
        node_type = "function"
      elif isinstance(node, libcst.ClassDef):
        node_type = "class"
      else:
        raise AIDocsEngineError(f"Unexpected node type: {node_type}")
      
      # Generate docstring (i.e. via OpenAI API wrapper function)
      docstring_value = self._config.generate_docstring_func(
        language="python",
        definition=node_source_code,
        definition_type=node_type,
        temperature=self._config.temperature,
      )

      # Return postprocessed docstring
      return postprocess_docstring(docstring_value)


  def insert_docstring(
    self,
    original_node: libcst.FunctionDef | libcst.ClassDef,
    updated_node: libcst.FunctionDef | libcst.ClassDef,
    docstring_data: FunctionDocstringData | ClassDocstringData,
  ) -> libcst.FunctionDef | libcst.ClassDef:
    assert isinstance(updated_node, (libcst.FunctionDef | libcst.ClassDef)), "Expected node to be a function or a class definition"
    assert isinstance(docstring_data, (FunctionDocstringData | ClassDocstringData)), "Expected docstring_data to be a function or a class docstring data object"

    # Detect the indentation of the function or class definition
    position_metadata = self.get_metadata(PositionProvider, original_node)
    start_position = position_metadata.start

    # Build docstring value
    docstring_value = build_numpy_docstring(
      data=docstring_data,
      overall_indent=start_position.column + self._config.indent_size,
      section_body_indent=self._config.indent_size,
    )

    # Add quotes around docstring value
    docstring_value = f"{self._config.quote_style}{docstring_value}{self._config.quote_style}"

    # Create docstring node
    docstring_node = libcst.SimpleStatementLine(body=[
      libcst.Expr(
        value=libcst.SimpleString(
          value=docstring_value,
        )
      )
    ])

    # Determine if function or class definition is a single line
    end_position = position_metadata.end
    is_single_line = start_position.line == end_position.line

    # Determine new body based on whether the function or class definition is a single line
    if is_single_line:
      # If definition was initially single line, then we need to add an empty line after the docstring
      new_body = libcst.IndentedBlock(
        body=[
          docstring_node,
          libcst.EmptyLine(),
          libcst.SimpleStatementLine(body=updated_node.body.body),
        ]
      )
    else:
      new_body = libcst.IndentedBlock(body=[docstring_node, libcst.EmptyLine()] + list(updated_node.body.body))

    # Return updated node
    return updated_node.with_changes(body=new_body)


  @override
  def leave_FunctionOrClassDef(
    self,
    original_node: libcst.FunctionDef | libcst.ClassDef,
    updated_node: libcst.FunctionDef | libcst.ClassDef,
  ) -> libcst.FunctionDef | libcst.ClassDef:
    # Skip if function or class already has docstring
    if check_if_node_has_docstring(updated_node):
      return updated_node

    # Generate docstring value
    docstring_data = self.generate_docstring(updated_node)

    # Insert docstring as first statement in function or class node
    updated_node = self.insert_docstring(original_node=original_node, updated_node=updated_node, docstring_data=docstring_data)

    # Return updated node
    return updated_node


  @override
  def leave_ClassDef(
    self,
    original_node: libcst.ClassDef,
    updated_node: libcst.ClassDef,
  ) -> libcst.ClassDef:
    return self.leave_FunctionOrClassDef(original_node, updated_node)


  @override
  def leave_FunctionDef(
    self,
    original_node: libcst.FunctionDef,
    updated_node: libcst.FunctionDef,
  ) -> libcst.FunctionDef:
    # Skip if function is an `__init__` function
    if self._config.skip_init_methods and updated_node.name.value == "__init__":
      return updated_node
    
    return self.leave_FunctionOrClassDef(original_node, updated_node)
