"""Model, repository and business rules: unit testing."""
from unittest.mock import Mock, MagicMock, AsyncMock
from math import nan, inf
import pytest
from student_testing.registry import (
    StudentError, InMemoryStudentRepository, StudentService, AsyncStudentService,
    make_student, find_by_last_name, filter_by_group, group_average, best_student,
)

pytestmark = pytest.mark.unit


def test_create_student(student):
    assert (student.student_id, student.first_name, student.group) == (1, "Марія", "ФЕП-32")


def test_strip_and_normalize():
    assert make_student(2, " Олена ", " Тест ", " феп-32 ", 80).group == "ФЕП-32"


@pytest.mark.parametrize("grade", [pytest.param(0, id="minimum"), 0.01, 50, 99.99, pytest.param(100, id="maximum")])
def test_valid_grades(grade):
    assert make_student(1, "А", "Б", "Г", grade).average_grade == pytest.approx(grade)


@pytest.mark.parametrize("grade", [-0.01, 100.01, nan, inf, -inf, "90", None, True])
def test_invalid_grades(grade):
    with pytest.raises(StudentError, match="Average grade"):
        make_student(1, "А", "Б", "Г", grade)


@pytest.mark.parametrize("first,last,group", [("", "Б", "Г"), ("А", "", "Г"), ("А", "Б", " "), (None, "Б", "Г")])
def test_required_fields(first, last, group):
    with pytest.raises(StudentError, match="required"):
        make_student(1, first, last, group, 80)


@pytest.mark.parametrize("id_value", [0, -1, "1", 2.0, True])
def test_invalid_student_id(id_value):
    with pytest.raises(StudentError, match="positive integer"):
        make_student(id_value, "А", "Б", "Г", 80)


def test_find_by_id(repository):
    assert repository.get(2).last_name == "Левицький"


def test_missing_id(repository):
    assert repository.get(999) is None


def test_last_name_casefold(students):
    assert [s.student_id for s in find_by_last_name(students, "дОРОШ")] == [1]


def test_group_filter_casefold(students):
    assert [s.student_id for s in filter_by_group(students, "феп-32")] == [1, 3]


def test_group_average_approx(students):
    assert group_average(students, "ФЕП-32") == pytest.approx(89.0)


def test_empty_group_average(students):
    assert group_average(students, "ФЕП-99") is None


def test_best_student(students):
    assert best_student(students).student_id == 2


def test_empty_best_student():
    assert best_student([]) is None


def test_best_student_tie_first(students):
    students.append(make_student(4, "Іван", "Коваль", "ФЕП-32", 95))
    assert best_student(students).student_id == 2


def test_duplicate_id_raises(repository, student):
    with pytest.raises(StudentError, match="Duplicate student ID") as exc_info:
        repository.add(student)
    assert "1" in str(exc_info.value)


def test_list_all_returns_copy(repository):
    returned = repository.list_all()
    returned.clear()
    assert len(repository.list_all()) == 3


def test_service_uses_mock_repository(student):
    repo = Mock(spec=InMemoryStudentRepository)
    repo.get.return_value = student
    assert StudentService(repo).get(1) == student
    repo.get.assert_called_once_with(1)


def test_register_notifier_interaction(student):
    repo = Mock(spec=InMemoryStudentRepository)
    notifier = Mock()
    notifier.notify.return_value = True
    service = StudentService(repo, notifier)
    assert service.register(student) == student
    repo.add.assert_called_once_with(student)
    notifier.notify.assert_called_once_with("Student registered: 1")


def test_register_without_notifier(student):
    repo = Mock(spec=InMemoryStudentRepository)
    assert StudentService(repo).register(student) is student
    repo.add.assert_called_once_with(student)


def test_repository_failure_propagates(student):
    repo = Mock(spec=InMemoryStudentRepository)
    notifier = Mock()
    repo.add.side_effect = OSError("storage unavailable")
    with pytest.raises(OSError, match="storage unavailable"):
        StudentService(repo, notifier).register(student)
    notifier.notify.assert_not_called()


def test_notifier_failure_propagates(student):
    repo = Mock(spec=InMemoryStudentRepository)
    notifier = MagicMock()
    notifier.notify.side_effect = RuntimeError("notification unavailable")
    with pytest.raises(RuntimeError, match="notification unavailable"):
        StudentService(repo, notifier).register(student)
    repo.add.assert_called_once_with(student)


def test_list_students_repository_return_value(student):
    repo = Mock(spec=InMemoryStudentRepository)
    repo.list_all.return_value = [student]
    assert StudentService(repo).list_students() == [student]
    repo.list_all.assert_called_once_with()


@pytest.mark.asyncio
async def test_async_student_service(student):
    repo = Mock()
    repo.get = AsyncMock(return_value=student)
    assert await AsyncStudentService(repo).load(1) == student
    repo.get.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_async_missing_student():
    repo = Mock()
    repo.get = AsyncMock(return_value=None)
    assert await AsyncStudentService(repo).load(42) is None
    repo.get.assert_awaited_once_with(42)


@pytest.mark.asyncio
async def test_async_invalid_id_never_awaited():
    repo = Mock()
    repo.get = AsyncMock()
    with pytest.raises(StudentError, match="positive"):
        await AsyncStudentService(repo).load(0)
    repo.get.assert_not_awaited()
