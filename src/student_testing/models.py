"""Validated student model and import counters."""
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class Student:
    student_id: int
    first_name: str
    last_name: str
    group: str
    average_grade: float

@dataclass(slots=True)
class ImportStatistics:
    total: int = 0
    valid: int = 0
    invalid: int = 0
    exported: int = 0
