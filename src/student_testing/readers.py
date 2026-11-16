"""Streaming CSV input without eagerly accumulating rows."""
import csv
from collections.abc import Iterator
from pathlib import Path
from student_testing.exceptions import DataImportError

FIELDS = ('student_id', 'first_name', 'last_name', 'group', 'average_grade')

def read_csv_rows(path: Path) -> Iterator[tuple[int, dict]]:
    try:
        with path.open('r', encoding='utf-8-sig', newline='') as stream:
            reader = csv.DictReader(stream, strict=True)
            if tuple(reader.fieldnames or ()) != FIELDS:
                raise DataImportError(f'Неправильний CSV header: {reader.fieldnames}')
            for row in reader:
                yield reader.line_num, row
    except (OSError, UnicodeError, csv.Error) as error:
        raise DataImportError(f'Не вдалося прочитати CSV: {path}') from error
