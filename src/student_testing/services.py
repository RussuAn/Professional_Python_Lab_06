"""Import policy, filtering, operation timing and counters."""
import logging
from collections.abc import Iterator
from contextlib import contextmanager
from time import perf_counter
from student_testing.models import Student, ImportStatistics
from student_testing.readers import read_csv_rows
from student_testing.validators import validate_student
from student_testing.exceptions import RecordValidationError
from pathlib import Path

@contextmanager
def logged_operation(name: str, logger: logging.Logger):
    started = perf_counter()
    logger.info('%s started', name)
    try:
        yield
    except Exception:
        logger.error('%s failed after %.6f s', name, perf_counter() - started)
        raise
    else:
        logger.info('%s finished in %.6f s', name, perf_counter() - started)

def import_students(path: Path, stats: ImportStatistics, *, skip_invalid: bool, logger: logging.Logger) -> Iterator[Student]:
    for line, row in read_csv_rows(path):
        stats.total += 1
        try:
            student = validate_student(row, line)
        except RecordValidationError as error:
            stats.invalid += 1
            logger.warning('Invalid record at line %s, field=%s: %s', error.line_number, error.field, error)
            if not skip_invalid:
                raise
            continue
        stats.valid += 1
        yield student

def filter_by_minimum(students: Iterator[Student], minimum_grade: float) -> Iterator[Student]:
    for student in students:
        if student.average_grade >= minimum_grade:
            yield student
