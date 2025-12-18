# S03 – eda_cli: мини-EDA для CSV

Небольшое CLI-приложение для базового анализа CSV-файлов.
Используется в рамках Семинара 03 курса «Инженерия ИИ».

## Требования

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) установлен в систему

## Инициализация проекта

В корне проекта (S03):

```bash
uv sync
```

Эта команда:

- создаст виртуальное окружение `.venv`;
- установит зависимости из `pyproject.toml`;
- установит сам проект `eda-cli` в окружение.

## Запуск CLI

### Краткий обзор

```bash
uv run eda-cli overview data/example.csv
```

Параметры:

- `--sep` – разделитель (по умолчанию `,`);
- `--encoding` – кодировка (по умолчанию `utf-8`).

### Полный EDA-отчёт

```bash
uv run eda-cli report data/example.csv --out-dir reports
```

В результате в каталоге `reports/` появятся:

- `report.md` – основной отчёт в Markdown;
- `summary.csv` – таблица по колонкам;
- `missing.csv` – пропуски по колонкам;
- `correlation.csv` – корреляционная матрица (если есть числовые признаки);
- `top_categories/*.csv` – top-k категорий по строковым признакам;
- `hist_*.png` – гистограммы числовых колонок;
- `missing_matrix.png` – визуализация пропусков;
- `correlation_heatmap.png` – тепловая карта корреляций.

## Тесты

```bash
uv run pytest -q
```
## HTTP API

Проект теперь включает HTTP-сервис на базе FastAPI для оценки качества датасетов. Запуск сервиса:uv run uvicorn eda_cli.api:app --reload --port 8000

Документация доступна по http://127.0.0.1:8000/docs (Swagger UI).

### Базовые эндпоинты (из семинара)
- **GET /health**: Проверяет статус сервиса. Возвращает JSON: `{"status": "ok", "service": "eda-cli-api", "version": "0.1.0"}`.
- **POST /quality**: Оценивает качество на основе агрегированных метрик. 
  - Запрос (JSON): `{"n_rows": int, "n_cols": int, "max_missing_share": float, "numeric_cols": int, "categorical_cols": int}`.
  - Ответ (JSON): `{"ok_for_model": bool, "quality_score": float, "message": str, "latency_ms": float, "flags": dict, "dataset_shape": dict}`.
- **POST /quality-from-csv**: Оценивает качество из загруженного CSV-файла.
  - Запрос: Multipart/form-data с файлом `file` (CSV).
  - Ответ: Аналогично /quality, но на основе реального датасета.

### Дополнительный эндпоинт (мой из HW04)
- **POST /quality-flags-from-csv**: Возвращает полный набор флагов качества датасета из CSV (включая мои доработки из HW03, такие как "has_constant_columns", "has_high_cardinality_categoricals").
  - Запрос: Multipart/form-data с файлом `file` (CSV).
  - Ответ (JSON): `{"flags": {"too_few_rows": bool, "too_many_missing": bool, ...}}` (список флагов зависит от реализации в core.py).
  - Пример использования: Загрузите CSV в Swagger UI или через curl/Postman.