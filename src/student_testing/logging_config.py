"""Consistent file/console event logging."""
import logging
from pathlib import Path
from student_testing.exceptions import ConfigurationError

def configure_logging(path: Path, level: str) -> logging.Logger:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(level=getattr(logging, level), format='%(asctime)s | %(levelname)s | %(message)s', handlers=[logging.FileHandler(path, encoding='utf-8'), logging.StreamHandler()], force=True)
    except OSError as error:
        raise ConfigurationError(f'Не вдалося створити log: {path}') from error
    return logging.getLogger('student_testing')
