from typing import Optional
import libcst
from libcst._nodes.statement import FunctionDef
from libcst.metadata import PositionProvider

from .utilities import col


StringQuoteLiteralStyles = ['"', "'", '"""', "'''"]


def preprocess_func_or_class_def(definition: str) -> str:
  assert isinstance(definition, str), "Expected definition to be a string"

  # TODO: try to minimize tokens passed to OpenAI API
  definition = definition.strip()

  return definition


def capitalize_first_letter(string: str) -> str:
  assert isinstance(string, str), "Expected string to be a string"

  string = string.strip()

  assert len(string) > 0, "Expected string to be non-empty"

  return string[0].upper() + string[1:]


def postprocess_docstring(docstring: str) -> str:
  assert isinstance(docstring, str), "Expected docstring to be a string"
  
  PREFIXES_TO_REMOVE = [
    "This function",
    "This method",
    "This class",
  ]

  # Remove leading prefixes from docstring
  for prefix in PREFIXES_TO_REMOVE:
    if docstring.startswith(prefix):
      docstring = docstring.removeprefix(prefix)
      break

  # Remove leading and trailing whitespace
  docstring = docstring.strip()

  # Capitalize first letter
  docstring = capitalize_first_letter(docstring)

  # TEMP
  docstring = f"AI: {docstring}"

  return docstring


def check_if_node_has_docstring(
  node: libcst.FunctionDef | libcst.ClassDef,
) -> bool:
  assert isinstance(node, (libcst.FunctionDef | libcst.ClassDef)), "Expected node to be a function or a class definition"

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
    generate_docstring_func: callable,
    skip_init_functions: bool,
    docstring_quote_style: str = '"""',
  ) -> None:
    assert isinstance(module, libcst.Module), "Expected module to be a `libcst.Module`"
    assert docstring_quote_style in StringQuoteLiteralStyles, "Expected docstring_quote_style to be a `StringQuoteLiteralStyles`"
    assert callable(generate_docstring_func), "Expected generate_docstring_func to be a callable"
    assert isinstance(skip_init_functions, bool), "Expected skip_init_functions to be a bool"

    # TEMP
    self.skipped_functions = []

    self._module = module
    self._docstring_quote_style = docstring_quote_style
    self._generate_docstring_func = generate_docstring_func
    self._skip_init_functions = skip_init_functions


  def leave_ClassDef(
    self,
    original_node: libcst.ClassDef,
    updated_node: libcst.ClassDef,
  ) -> libcst.ClassDef:
    # Skip if class already has docstring
    if check_if_node_has_docstring(updated_node):
      return updated_node
    
    # Generate docstring value
    docstring_value = self.generate_docstring(updated_node)

    # Insert docstring as first statement in class node
    updated_node = self.insert_docstring(original_node=original_node, updated_node=updated_node, docstring_value=docstring_value)
    
    # Return updated node
    return updated_node


  def leave_FunctionDef(
    self,
    original_node: libcst.FunctionDef,
    updated_node: libcst.FunctionDef,
  ) -> libcst.FunctionDef:
    # Skip if function is an `__init__` function
    if self._skip_init_functions and updated_node.name.value == "__init__":
      return updated_node

    # Skip if function already has docstring
    if check_if_node_has_docstring(updated_node):
      self.skipped_functions.append(updated_node.name.value)
      return updated_node
    
    # Generate docstring value
    docstring_value = self.generate_docstring(updated_node)

    # Insert docstring as first statement in function node
    updated_node = self.insert_docstring(original_node=original_node, updated_node=updated_node, docstring_value=docstring_value)
    
    # Return updated node
    return updated_node


  def extract_node_source_code(
    self,
    node: libcst.FunctionDef | libcst.ClassDef,
  ) -> str:
      assert isinstance(node, (libcst.FunctionDef | libcst.ClassDef)), "Expected node to be a function or a class definition"
      
      node_source_code = self._module.code_for_node(node)
      
      return node_source_code


  def generate_docstring(
    self,
    node: libcst.FunctionDef | libcst.ClassDef,
  ) -> str:
      assert isinstance(node, (libcst.FunctionDef | libcst.ClassDef)), "Expected node to be a function or a class definition"

      print(f"Generating docstring value for: `{col(node.name.value, 'blue')}`")
      
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
        raise Exception(f"Unexpected node type: {node_type}")
      
      # Generate docstring (i.e. via OpenAI API wrapper function)
      docstring_value = self._generate_docstring_func(node_source_code, node_type)

      # Postprocess generated docstring
      docstring_value = postprocess_docstring(docstring_value)

      # Print docstring
      print(f"Generated docstring:", col(docstring_value, "green"))

      return docstring_value


  def insert_docstring(
    self,
    original_node: libcst.FunctionDef | libcst.ClassDef,
    updated_node: libcst.FunctionDef | libcst.ClassDef,
    docstring_value: str,
  ) -> libcst.FunctionDef:
    assert isinstance(updated_node, (libcst.FunctionDef | libcst.ClassDef)), "Expected node to be a function or a class definition"
    assert isinstance(docstring_value, str), "Expected docstring_value to be a string"

    # Create docstring node
    docstring_node = libcst.SimpleStatementLine(body=[
      libcst.Expr(value=libcst.SimpleString(value=f'{self._docstring_quote_style}{docstring_value}{self._docstring_quote_style}')),
    ])

    # Determine if function or class definition is a single line
    position_metadata = self.get_metadata(PositionProvider, original_node)
    start_position = position_metadata.start
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
