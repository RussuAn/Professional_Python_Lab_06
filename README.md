# Система обліку студентів

Лабораторна робота №6 «Автоматизоване тестування Python-програм»  
Курс «Професійний Python», варіант №1  
Руссу Анастасія Сергіївна, ФЕП-32  
Викладач: Свелеба С. А.

## Опис роботи

Створено систему автоматизованого тестування проєкту обліку студентів, що продовжує попередні лабораторні роботи. Перевіряються створення й валідація студентів, пошук за ID і прізвищем, фільтрація за групою, розрахунок середнього бала, найкращий студент, імпорт CSV, експорт JSON, YAML-конфігурація, помилки залежностей та асинхронний сервіс. Тести написано на pytest; застосовано fixtures, параметризацію, tmp_path, monkeypatch, Mock, MagicMock та AsyncMock. Окремо аналізується покриття рядків і гілок.

## Структура проєкту

```text
Lab_06_variant_1/
├── pyproject.toml
├── README.md
├── .gitignore
├── config.yaml
├── data/students.csv
├── report/Report_lab_06.docx
├── src/student_testing/
│   ├── __init__.py
│   ├── models.py
│   ├── exceptions.py
│   ├── validators.py
│   ├── readers.py
│   ├── exporters.py
│   ├── config.py
│   ├── services.py
│   ├── registry.py
│   ├── cli.py
│   └── main.py
└── tests/
    ├── conftest.py
    ├── unit/
    │   ├── test_registry.py
    │   └── test_io.py
    └── integration/
        └── test_pipeline.py
```

## Запуск у Windows

У Visual Studio Code відкрийте папку `Lab_06_variant_1`. У PowerShell з кореня проєкту виконайте послідовно:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m student_testing.cli
```

## Перевірка типів і тести

```powershell
.\.venv\Scripts\python.exe -m pytest -v
.\.venv\Scripts\python.exe -m pytest tests\unit -v
.\.venv\Scripts\python.exe -m pytest tests\integration -v
```

## Експерименти та coverage

```powershell
.\.venv\Scripts\python.exe -m pytest --cov=student_testing --cov-report=term-missing
.\.venv\Scripts\python.exe -m pytest --cov=student_testing --cov-branch --cov-report=term-missing --cov-report=html
start htmlcov\index.html
```

Результати поточного запуску й кількість перевірок наведені в звіті. Для захисту використовуйте власний запуск команд у Windows PowerShell: час і coverage можуть незначно відрізнятися залежно від версій Python та бібліотек.

## Обробка даних

Оцінка має бути скінченним числом від 0 до 100, ID — додатним цілим числом, обов'язкові рядкові поля — непорожніми. Пошук за прізвищем і групою нечутливий до регістру. Для порожнього набору середній бал групи та найкращий студент дорівнюють `None`. CSV читається потоково, JSON зберігається атомарно, а помилки конфігурації та записів обробляються через власні винятки.
