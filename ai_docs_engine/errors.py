class AIDocsEngineError(Exception):
  """
  This is the base class for any Exception that is intentionally raised
  from within the project, that way they can all be caught together.
  """
  pass


class AIDocsEngineTooManyTokensError(AIDocsEngineError):
  def __init__(self) -> None:
    super().__init__(f"There is no OpenAI API model that can handle this many tokens, and I have not yet implemented the logic to pre-process the input to fit within the OpenAI API limits.")
