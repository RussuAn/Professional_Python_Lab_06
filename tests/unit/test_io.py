"""Unit-level validation, error-path and configuration checks."""
import json
import logging
from pathlib import Path
from unittest.mock import Mock
import pytest
from student_testing.models import Student, ImportStatistics
from student_testing.readers import read_csv_rows, FIELDS
from student_testing.validators import validate_student
from student_testing.services import import_students, filter_by_minimum, logged_operation
from student_testing.config import load_config
from student_testing.exporters import export_json_atomic
from student_testing.exceptions import DataImportError, ConfigurationError, RecordValidationError

pytestmark = pytest.mark.unit


def row(*values):
    return dict(zip(FIELDS, values))


def test_csv_validation_success():
    assert validate_student(row("1", " Марія ", " Дорош ", "ФЕП-32", "91.50"), 2) == Student(1,"Марія","Дорош","ФЕП-32",91.5)


@pytest.mark.parametrize("grade", ["-0.01", "100.01", "NaN", "inf", "abc"])
def test_csv_bad_grade(grade):
    with pytest.raises(RecordValidationError) as e:
        validate_student(row("1","Марія","Дорош","ФЕП-32",grade), 7)
    assert e.value.field == "average_grade"
    assert e.value.line_number == 7


def test_csv_numeric_exception_chaining():
    with pytest.raises(RecordValidationError) as e:
        validate_student(row("1", "А", "Б", "Г", "bad"), 3)
    assert isinstance(e.value.__cause__, ValueError)


def test_csv_id_exception_chaining():
    with pytest.raises(RecordValidationError) as e:
        validate_student(row("bad", "А", "Б", "Г", "50"), 3)
    assert e.value.field == "student_id"
    assert isinstance(e.value.__cause__, ValueError)


def test_csv_extra_field():
    data = row("1", "А", "Б", "Г", "50")
    data[None] = ["extra"]
    with pytest.raises(RecordValidationError):
        validate_student(data, 2)


def test_csv_missing_field():
    data = row("1", "А", "Б", "Г", "50")
    del data["group"]
    with pytest.raises(RecordValidationError):
        validate_student(data, 2)


def test_import_missing_file(tmp_path):
    with pytest.raises(DataImportError) as e:
        list(read_csv_rows(tmp_path / "absent.csv"))
    assert isinstance(e.value.__cause__, FileNotFoundError)


def test_import_wrong_csv_header(tmp_path):
    path = tmp_path / "data.csv"
    path.write_text("id,name\n1,Maria\n",encoding="utf-8")
    with pytest.raises(DataImportError):
        list(read_csv_rows(path))


def test_import_malformed_csv(tmp_path, csv_header):
    path = tmp_path / "bad.csv"
    path.write_text(csv_header + '1,"unfinished,A,G,90\n',encoding="utf-8")
    with pytest.raises(DataImportError):
        list(read_csv_rows(path))


def test_filter_includes_grade_boundary():
    values = iter([Student(1,"А","Б","Г",59.99), Student(2,"В","Г","Г",60.0)])
    assert [s.student_id for s in filter_by_minimum(values,60)] == [2]


def test_export_unicode_json(tmp_path, student):
    dest = tmp_path / "out.json"
    stats=ImportStatistics()
    export_json_atomic(iter([student]),dest,stats)
    content=dest.read_text(encoding="utf-8")
    assert "Марія" in content
    assert json.loads(content)[0]["student_id"]==1
    assert stats.exported==1


def test_atomic_export_preserves_original(tmp_path, student):
    dest=tmp_path / "result.json"
    dest.write_text("before",encoding="utf-8")
    def broken():
        yield student
        raise RecordValidationError("broken input",line_number=3)
    with pytest.raises(RecordValidationError):
        export_json_atomic(broken(), dest, ImportStatistics())
    assert dest.read_text(encoding="utf-8")=="before"
    assert not list(tmp_path.glob(".students-*.tmp"))


def test_yaml_bad_syntax(tmp_path):
    path=tmp_path/"bad.yaml"
    path.write_text("input: [broken\n",encoding="utf-8")
    with pytest.raises(ConfigurationError):
        load_config(path)


def test_yaml_missing_file(tmp_path):
    with pytest.raises(ConfigurationError) as e:
        load_config(tmp_path/"missing.yaml")
    assert isinstance(e.value.__cause__, FileNotFoundError)


def test_monkeypatch_environment(tmp_path,monkeypatch):
    monkeypatch.setenv("LAB06_MODE","testing")
    import os
    assert os.environ["LAB06_MODE"] == "testing"
    monkeypatch.delenv("LAB06_MODE")
    assert os.getenv("LAB06_MODE") is None


def test_monkeypatch_function(tmp_path,monkeypatch):
    from student_testing import readers
    def fake_rows(_path):
        yield 2, row("1", "Іван", "Тест", "ФЕП-32", "90")
    monkeypatch.setattr(readers,"read_csv_rows",fake_rows)
    assert list(readers.read_csv_rows(tmp_path/"missing.csv"))[0][1]["student_id"]=="1"


def test_logged_operation_success():
    logger=Mock(spec=logging.Logger)
    with logged_operation("read",logger):
        assert True
    logger.info.assert_called()
    logger.error.assert_not_called()


def test_logged_operation_error():
    logger=Mock(spec=logging.Logger)
    with pytest.raises(RuntimeError):
        with logged_operation("read",logger):
            raise RuntimeError("failed")
    logger.error.assert_called_once()


def test_yield_fixture_file(file_resource):
    assert file_resource.read_text(encoding="utf-8")=="ready"
