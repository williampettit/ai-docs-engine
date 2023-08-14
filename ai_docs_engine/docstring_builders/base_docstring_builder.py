from ai_docs_engine.docstring_schema import ClassDocstringData, FunctionDocstringData


class BaseDocstringBuilder:
  def __call__(
    self,
    data: FunctionDocstringData | ClassDocstringData,
    indent_char: str,
  ) -> str:
    raise NotImplementedError()
