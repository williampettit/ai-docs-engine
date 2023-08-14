import logging
from typing import Optional

try:
  from termcolor import colored as col
except ImportError:
  col = lambda text, *_: text


class CustomFormatter(logging.Formatter):
  def __init__(
    self,
    include_func_name: bool = False,
    date_color: Optional[str] = "yellow",
  ) -> None:
    fmt = "%(asctime)s %(levelname)s %(message)s"
    if include_func_name: fmt += " (%(funcName)s)"
    super().__init__(fmt=fmt, datefmt=col("%H:%M:%S", date_color))

  def format(self, record: logging.LogRecord) -> str:
    LEVEL_COLORS = {
      logging.DEBUG:    "magenta",
      logging.INFO:     "cyan",
      logging.WARNING:  "yellow",
      logging.ERROR:    "red",
      logging.CRITICAL: "red",
    }

    # Colorize log record
    record.funcName = col(record.funcName, "cyan")
    record.levelname = col(f"{record.levelname}", LEVEL_COLORS.get(record.levelno, "white"))

    # Return formatted log record
    return super().format(record)


# Configure logging
logging.basicConfig(
  level=logging.INFO,
  handlers=[],
)

# Create logger instance
logger = logging.getLogger("ai_docs_engine")

# Create stream handler and set formatter
ch = logging.StreamHandler()
ch.setFormatter(CustomFormatter(date_color="light_cyan"))

# Add handler to logger
logger.addHandler(ch)
