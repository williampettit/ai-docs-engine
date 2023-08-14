from ai_docs_engine.docstring_schema import ClassDocstringData, FunctionDocstringData
from ai_docs_engine.docstring_builders.base_docstring_builder import BaseDocstringBuilder


class NumpyDocstringBuilder(BaseDocstringBuilder):
  def __call__(
    self,
    data: FunctionDocstringData | ClassDocstringData,
    indent_char: str,
  ) -> str:
    assert isinstance(data, (FunctionDocstringData, ClassDocstringData)), "Expected data to be a function or a class docstring data object"
    assert isinstance(indent_char, str), "Expected indent_char to be a string"

    lines = [data.description]
    section_indent = indent_char

    if isinstance(data, FunctionDocstringData):
      lines.extend(self._build_section("Parameters", data.parameters, section_indent))
      lines.extend(self._build_section("Returns", data.return_values, section_indent))
      lines.extend(self._build_section("Raises", data.exceptions, section_indent))

    lines = "\n".join(lines)
    return f"\n{lines}\n\n"

  @staticmethod
  def _build_section(title: str, items: list, section_indent: str) -> list:
    if not items:
      return []

    section_lines = [title, "-" * len(title)]
    for item in items:
      section_lines.append(f"{section_indent}{item.name or 'value'} : {item.assumed_type}")
      section_lines.append(f"{section_indent}{section_indent}{item.description}")

    return ["", *section_lines]
