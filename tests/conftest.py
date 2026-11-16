"""Reusable pytest fixtures with isolated data and controlled cleanup."""
from pathlib import Path
import pytest
from student_testing.registry import InMemoryStudentRepository, make_student


@pytest.fixture
def student():
    return make_student(1, "Марія", "Дорош", "ФЕП-32", 86.5)


@pytest.fixture
def students():
    return [
        make_student(1, "Марія", "Дорош", "ФЕП-32", 86.5),
        make_student(2, "Данило", "Левицький", "ФЕП-31", 95.0),
        make_student(3, "Соломія", "Климчук", "ФЕП-32", 91.5),
    ]


@pytest.fixture
def repository(students):
    return InMemoryStudentRepository(students)


@pytest.fixture
def file_resource(tmp_path: Path):
    """Yield fixture illustrates setup and teardown with a real temporary file."""
    path = tmp_path / "session.txt"
    path.write_text("ready", encoding="utf-8")
    yield path
    path.unlink(missing_ok=True)


@pytest.fixture(scope="module")
def csv_header():
    return "student_id,first_name,last_name,group,average_grade\n"
