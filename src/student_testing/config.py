"""Fail-fast loading and validation of YAML configuration."""
from dataclasses import dataclass
from pathlib import Path
import yaml
from student_testing.exceptions import ConfigurationError

@dataclass(frozen=True, slots=True)
class AppConfig:
    input_path: Path
    output_path: Path
    log_path: Path
    minimum_grade: float
    skip_invalid: bool
    log_level: str

def load_config(path: Path) -> AppConfig:
    try:
        with path.open('r', encoding='utf-8') as stream:
            settings = yaml.safe_load(stream)
    except (OSError, yaml.YAMLError) as error:
        raise ConfigurationError(f'Не вдалося прочитати YAML: {path}') from error
    try:
        if not isinstance(settings, dict):
            raise ValueError('Корінь YAML повинен бути mapping')
        input_path = settings['input']['path']
        output_path = settings['output']['path']
        log_path = settings['logging']['path']
        level = settings['logging']['level']
        minimum = settings['processing']['minimum_grade']
        skip = settings['processing']['skip_invalid']
        if not all(isinstance(v, str) and v.strip() for v in (input_path, output_path, log_path, level)):
            raise ValueError('Шляхи й рівень логування повинні бути непорожніми рядками')
        if type(minimum) not in (int, float) or not 0 <= minimum <= 100:
            raise ValueError('minimum_grade повинен бути числом від 0 до 100')
        if type(skip) is not bool:
            raise ValueError('skip_invalid повинен бути boolean')
        if level.upper() not in {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}:
            raise ValueError('Невідомий рівень logging')
        root = path.resolve().parent
        def resolve(raw: str) -> Path:
            p = Path(raw)
            return p if p.is_absolute() else root / p
        incoming = resolve(input_path)
        outgoing = resolve(output_path)
        logs = resolve(log_path)
        if not incoming.is_file():
            raise ValueError(f'Input file не існує: {incoming}')
        if incoming.resolve() == outgoing.resolve():
            raise ValueError('Input та output повинні відрізнятися')
        return AppConfig(incoming, outgoing, logs, float(minimum), skip, level.upper())
    except (KeyError, TypeError, ValueError) as error:
        raise ConfigurationError(f'Некоректна конфігурація: {error}') from error
