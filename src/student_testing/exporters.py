"""Streaming JSON array and atomic replace on successful completion."""
import json
import os
import tempfile
from dataclasses import asdict
from collections.abc import Iterable
from pathlib import Path
from student_testing.models import Student, ImportStatistics
from student_testing.exceptions import DataExportError

def export_json_atomic(students: Iterable[Student], destination: Path, stats: ImportStatistics) -> None:
    temporary: Path | None = None
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='', dir=destination.parent, prefix='.students-', suffix='.tmp', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write('[\n')
            first = True
            for student in students:
                if not first:
                    stream.write(',\n')
                json.dump(asdict(student), stream, ensure_ascii=False, indent=2)
                stats.exported += 1
                first = False
            stream.write('\n]\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    except OSError as error:
        raise DataExportError(f'Не вдалося виконати atomic export до {destination}') from error
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
