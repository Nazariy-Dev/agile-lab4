# agile-lab4

[![CI](https://github.com/Nazariy-Dev/agile-lab4/actions/workflows/ci.yml/badge.svg)](https://github.com/Nazariy-Dev/agile-lab4/actions/workflows/ci.yml)

Лабораторна робота 4 «Тестування та інтеграція у гнучких технологіях»
з дисципліни «Гнучкі технології розробки програмного забезпечення».
Виконав: Попцов Назарій Юрійович, група Б-121-23-2-ПІ.

`agile_metrics.py` – модуль розрахунку Agile-метрик з лабораторних робіт 1–3:
ємність команди, відбір завдань у спринт із залежностями, пріоритет V/SP,
velocity, прогноз кількості спринтів, lead/cycle time, закон Літтла.

## Запуск локально

```bash
python -m venv .venv
. .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
ruff check .
pytest --cov --cov-report=term-missing
```

## CI

GitHub Actions (`.github/workflows/ci.yml`) запускається на кожен push у `main`
і на кожен pull request: лінтер ruff, тести PyTest із покриттям (поріг 90 %)
на Python 3.11, 3.12, 3.13, підсумок покриття і артефакти `report.xml`, `coverage.xml`.
