"""Student accounting services with typed dependency protocols."""
from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol
from dataclasses import dataclass
from math import isfinite

from student_testing.models import Student


class StudentRepository(Protocol):
    def add(self, student: Student) -> None: ...
    def get(self, student_id: int) -> Student | None: ...
    def list_all(self) -> list[Student]: ...


class Notifier(Protocol):
    def notify(self, message: str) -> bool: ...


class StudentError(ValueError):
    """Invalid or duplicated domain student data."""


class InMemoryStudentRepository:
    """Small deterministic in-memory repository for the lab."""
    def __init__(self, students: Iterable[Student] = ()) -> None:
        self._students: dict[int, Student] = {}
        for student in students:
            self.add(student)

    def add(self, student: Student) -> None:
        if student.student_id in self._students:
            raise StudentError(f"Duplicate student ID: {student.student_id}")
        self._students[student.student_id] = student

    def get(self, student_id: int) -> Student | None:
        return self._students.get(student_id)

    def list_all(self) -> list[Student]:
        return list(self._students.values())


def make_student(student_id: int, first_name: str, last_name: str, group: str, average_grade: float) -> Student:
    """Validate programmatically created students using the same data contract as CSV."""
    if type(student_id) is not int or student_id <= 0:
        raise StudentError("Student ID must be a positive integer")
    if not all(isinstance(x, str) and x.strip() for x in (first_name, last_name, group)):
        raise StudentError("First name, last name and group are required")
    if type(average_grade) not in (int, float) or not isfinite(average_grade) or not 0 <= average_grade <= 100:
        raise StudentError("Average grade must be finite and between 0 and 100")
    return Student(student_id, first_name.strip(), last_name.strip(), group.strip().upper(), float(average_grade))


def find_by_last_name(students: Iterable[Student], surname: str) -> list[Student]:
    return [s for s in students if s.last_name.casefold() == surname.strip().casefold()]


def filter_by_group(students: Iterable[Student], group: str) -> list[Student]:
    return [s for s in students if s.group.casefold() == group.strip().casefold()]


def group_average(students: Iterable[Student], group: str) -> float | None:
    selected = filter_by_group(students, group)
    return sum(s.average_grade for s in selected) / len(selected) if selected else None


def best_student(students: Iterable[Student]) -> Student | None:
    return max(students, key=lambda s: s.average_grade, default=None)


class StudentService:
    """Business service: storage and optional notification are injected dependencies."""
    def __init__(self, repository: StudentRepository, notifier: Notifier | None = None) -> None:
        self.repository = repository
        self.notifier = notifier

    def register(self, student: Student) -> Student:
        self.repository.add(student)
        if self.notifier is not None:
            self.notifier.notify(f"Student registered: {student.student_id}")
        return student

    def get(self, student_id: int) -> Student | None:
        return self.repository.get(student_id)

    def list_students(self) -> list[Student]:
        return self.repository.list_all()


class AsyncStudentRepository(Protocol):
    async def get(self, student_id: int) -> Student | None: ...


class AsyncStudentService:
    def __init__(self, repository: AsyncStudentRepository) -> None:
        self.repository = repository

    async def load(self, student_id: int) -> Student | None:
        if student_id <= 0:
            raise StudentError("Student ID must be positive")
        return await self.repository.get(student_id)
