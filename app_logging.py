import logging
from pathlib import Path


DEFAULT_LOG_PATH = Path("logs/app.log")


def configure_logging(log_path: str | Path = DEFAULT_LOG_PATH) -> None:
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=path,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def app_logger() -> logging.Logger:
    return logging.getLogger("resume_ai")
