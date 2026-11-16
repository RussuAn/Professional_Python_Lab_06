"""Full integrated paths using real isolated CSV, YAML, JSON and services."""
import json
import logging
from pathlib import Path
from unittest.mock import Mock, AsyncMock
import pytest
from student_testing.models import Student, ImportStatistics
from student_testing.registry import (InMemoryStudentRepository, StudentService, AsyncStudentService,
    make_student, group_average, best_student)
from student_testing.services import import_students
from student_testing.exceptions import RecordValidationError, ConfigurationError
from student_testing.config import load_config
from student_testing.main import run

pytestmark = pytest.mark.integration


def write_config(tmp_path, data, *, minimum=60, skip=True):
    input_path=tmp_path/'students.csv'
    input_path.write_text(data,encoding="utf-8")
    cfg=tmp_path/'config.yaml'
    cfg.write_text(f"input:\n  path: students.csv\noutput:\n  path: result.json\nlogging:\n  path: app.log\n  level: INFO\nprocessing:\n  minimum_grade: {minimum}\n  skip_invalid: {'true' if skip else 'false'}\n",encoding="utf-8")
    return cfg


def test_import_validate_export_report(tmp_path,csv_header):
    cfg=write_config(tmp_path,csv_header + "1,Марія,Дорош,ФЕП-32,86.5\n2,Данило,Левицький,ФЕП-31,95\n3,Іван,Тест,ФЕП-32,error\n4,Олена,Романюк,ФЕП-33,40\n")
    loaded=load_config(cfg)
    assert loaded.minimum_grade==60
    stats=run(cfg)
    assert (stats.total,stats.valid,stats.invalid,stats.exported)==(4,3,1,2)
    exported=json.loads((tmp_path/'result.json').read_text(encoding="utf-8"))
    assert [s['student_id'] for s in exported]==[1,2]
    assert 'Invalid record' in (tmp_path/'app.log').read_text(encoding='utf-8')


def test_strict_import_does_not_replace_existing_output(tmp_path,csv_header):
    cfg=write_config(tmp_path,csv_header+"1,Марія,Дорош,ФЕП-32,90\n2,Остап,Мазур,ФЕП-31,bad\n",skip=False)
    previous=tmp_path/'result.json'
    previous.write_text('{"previous":true}',encoding='utf-8')
    with pytest.raises(RecordValidationError):
        run(cfg)
    assert previous.read_text(encoding='utf-8')=='{"previous":true}'


def test_config_rejects_invalid_grade_threshold(tmp_path,csv_header):
    cfg=write_config(tmp_path,csv_header+'1,А,Б,Г,90\n',minimum=120)
    with pytest.raises(ConfigurationError):
        load_config(cfg)


def test_import_to_repository_and_domain_report(tmp_path,csv_header):
    path=tmp_path/'records.csv'
    path.write_text(csv_header + "1,Марія,Дорош,ФЕП-32,86.5\n2,Соломія,Климчук,ФЕП-32,91.5\n",encoding='utf-8')
    imported=list(import_students(path,ImportStatistics(),skip_invalid=False,logger=logging.getLogger('lab06.integration')))
    repo=InMemoryStudentRepository()
    service=StudentService(repo)
    for student in imported:
        service.register(student)
    assert group_average(service.list_students(),'ФЕП-32')==pytest.approx(89.0)
    assert best_student(service.list_students()).student_id==2


@pytest.mark.asyncio
async def test_async_repository_integration_after_csv_import(tmp_path,csv_header):
    path=tmp_path/'students.csv'
    path.write_text(csv_header + '5,Марія,Дорош,ФЕП-32,85\n',encoding='utf-8')
    students=list(import_students(path,ImportStatistics(),skip_invalid=False,logger=logging.getLogger('lab06.async')))
    db={s.student_id:s for s in students}
    repo=Mock()
    async def get(student_id):
        return db.get(student_id)
    repo.get=AsyncMock(side_effect=get)
    loaded=await AsyncStudentService(repo).load(5)
    assert loaded==students[0]
    repo.get.assert_awaited_once_with(5)
