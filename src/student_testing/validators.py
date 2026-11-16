"""Parse and validate the five columns of variant 1."""
from math import isfinite
from student_testing.models import Student
from student_testing.exceptions import RecordValidationError

def validate_student(row: dict, line_number: int) -> Student:
    if None in row or any(row.get(name) is None for name in ('student_id','first_name','last_name','group','average_grade')):
        raise RecordValidationError('Невірна кількість CSV полів', line_number=line_number)
    try:
        student_id = int(row['student_id'].strip())
    except (ValueError, TypeError, AttributeError) as error:
        raise RecordValidationError('Некоректний student_id', line_number=line_number, field='student_id') from error
    if student_id <= 0:
        raise RecordValidationError('student_id повинен бути додатним', line_number=line_number, field='student_id')
    fields = {k: row[k].strip() for k in ('first_name', 'last_name', 'group')}
    for field, value in fields.items():
        if not value:
            raise RecordValidationError(f'Порожнє поле {field}', line_number=line_number, field=field)
    try:
        grade = float(row['average_grade'].strip())
    except (ValueError, TypeError, AttributeError) as error:
        raise RecordValidationError('average_grade не є числом', line_number=line_number, field='average_grade') from error
    if not isfinite(grade) or not 0 <= grade <= 100:
        raise RecordValidationError('average_grade повинен бути в межах 0–100', line_number=line_number, field='average_grade')
    return Student(student_id, fields['first_name'], fields['last_name'], fields['group'], grade)
