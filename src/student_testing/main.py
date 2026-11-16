"""CLI entry point: python -m student_testing.main."""
import argparse
import logging
from pathlib import Path
from student_testing.config import load_config
from student_testing.exceptions import ApplicationError
from student_testing.exporters import export_json_atomic
from student_testing.logging_config import configure_logging
from student_testing.models import ImportStatistics
from student_testing.services import filter_by_minimum, import_students, logged_operation

def run(config_file: Path) -> ImportStatistics:
    config = load_config(config_file)
    logger = configure_logging(config.log_path, config.log_level)
    stats = ImportStatistics()
    try:
        with logged_operation('Student import/export', logger):
            students = import_students(config.input_path, stats, skip_invalid=config.skip_invalid, logger=logger)
            export_json_atomic(filter_by_minimum(students, config.minimum_grade), config.output_path, stats)
    except ApplicationError:
        logger.error('Processing aborted: total=%s, valid=%s, invalid=%s, exported_attempted=%s', stats.total, stats.valid, stats.invalid, stats.exported)
        raise
    logger.info('Total=%d, valid=%d, invalid=%d, exported=%d', stats.total, stats.valid, stats.invalid, stats.exported)
    return stats

def main() -> int:
    parser = argparse.ArgumentParser(description='Lab 05 — student CSV → JSON')
    parser.add_argument('--config', type=Path, default=Path('config.yaml'))
    args = parser.parse_args()
    try:
        stats = run(args.config)
    except ApplicationError as error:
        logging.getLogger('student_testing').error('%s (cause=%s)', error, type(error.__cause__).__name__ if error.__cause__ else 'none')
        return 1
    print(f'РЕЗУЛЬТАТ: total={stats.total}; valid={stats.valid}; invalid={stats.invalid}; exported={stats.exported}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
