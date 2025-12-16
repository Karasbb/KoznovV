from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd
import typer

from .core import (
    DatasetSummary,
    compute_quality_flags,
    correlation_matrix,
    flatten_summary_for_print,
    missing_table,
    summarize_dataset,
    top_categories,
)
from .viz import (
    plot_correlation_heatmap,
    plot_missing_matrix,
    plot_histograms_per_column,
    save_top_categories_tables,
)

app = typer.Typer(help="Мини-CLI для EDA CSV-файлов")


def _load_csv(
    path: Path,
    sep: str = ",",
    encoding: str = "utf-8",
) -> pd.DataFrame:
    if not path.exists():
        raise typer.BadParameter(f"Файл '{path}' не найден")
    try:
        return pd.read_csv(path, sep=sep, encoding=encoding)
    except Exception as exc:  # noqa: BLE001
        raise typer.BadParameter(f"Не удалось прочитать CSV: {exc}") from exc


@app.command()
def overview(
    path: str = typer.Argument(..., help="Путь к CSV-файлу."),
    sep: str = typer.Option(",", help="Разделитель в CSV."),
    encoding: str = typer.Option("utf-8", help="Кодировка файла."),
) -> None:
    """
    Напечатать краткий обзор датасета:
    - размеры;
    - типы;
    - простая табличка по колонкам.
    """
    df = _load_csv(Path(path), sep=sep, encoding=encoding)
    summary: DatasetSummary = summarize_dataset(df)
    summary_df = flatten_summary_for_print(summary)

    typer.echo(f"Строк: {summary.n_rows}")
    typer.echo(f"Столбцов: {summary.n_cols}")
    typer.echo("\nКолонки:")
    typer.echo(summary_df.to_string(index=False))


@app.command()
def report(
    path: str = typer.Argument(..., help="Путь к CSV-файлу."),
    out_dir: str = typer.Option("reports", help="Каталог для отчёта."),
    sep: str = typer.Option(",", help="Разделитель в CSV."),
    encoding: str = typer.Option("utf-8", help="Кодировка файла."),
    max_hist_columns: int = typer.Option(6, help="Максимум числовых колонок для гистограмм."),
    top_k_categories: int = typer.Option(5, help="Количество топ-значений для категориальных колонок."),
    title: str = typer.Option("EDA Report", help="Заголовок отчёта."),
) -> None:
    """
    Сгенерировать полный EDA-отчёт:
    - текстовый overview и summary по колонкам (CSV/Markdown);
    - статистика пропусков;
    - корреляционная матрица;
    - top-k категорий по категориальным признакам;
    - картинки: гистограммы, матрица пропусков, heatmap корреляции.
    """
    out_root = Path(out_dir)
    out_root.mkdir(parents=True, exist_ok=True)
    df = _load_csv(Path(path), sep=sep, encoding=encoding)

    summary = summarize_dataset(df)
    missing_df = missing_table(df)
    flags = compute_quality_flags(summary, missing_df)
    corr = correlation_matrix(df)
    top_cats = top_categories(df, k=top_k_categories)

    # Визуализации (предполагаю функции из viz.py; если имен нет — подправь)
    plot_histograms(df, out_root, max_cols=max_hist_columns)
    plot_missing_matrix(missing_df, out_root)
    plot_correlation_heatmap(corr, out_root)

    # Запись таблиц в CSV (для отчета)
    summary_flattened = flatten_summary_for_print(summary)  # Если flatten есть в core.py
    summary_flattened.to_csv(out_root / "summary.csv", index=False)
    missing_df.to_csv(out_root / "missing.csv", index=False)
    corr.to_csv(out_root / "correlation.csv", index=False)
    top_cats.to_csv(out_root / "top_categories.csv", index=False)

    # Запись в report.md с title и параметрами
    report_md = out_root / "report.md"
    with open(report_md, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        f.write(f"Параметры: Top K категорий: {top_k_categories}\n\n")
        f.write("## Обзор данных\n")
        f.write(summary_flattened.to_markdown(index=False) + "\n\n")  # Таблица summary в md
        f.write("## Пропуски\n")
        f.write(missing_df.to_markdown(index=False) + "\n\n")  # Таблица пропусков
        f.write("## Качество данных\n")
        f.write(f"Флаги качества: {flags}\n\n")  # Флаги, включая новые эвристики
        f.write(f"Интегральный score: {flags['quality_score']}\n\n")
        f.write("## Корреляция\n")
        f.write(corr.to_markdown() + "\n\n")  # Таблица корреляции
        f.write("![Корреляционная тепловая карта](correlation_heatmap.png)\n\n")  # Ссылка на график
        f.write("## Топ категории\n")
        f.write(top_cats.to_markdown(index=False) + "\n\n")  # Топ категории с k
        f.write("## Гистограммы\n")
        f.write("![Гистограммы](histograms.png)\n\n")  # Ссылка на график
        f.write("## Матрица пропусков\n")
        f.write("![Матрица пропусков](missing_matrix.png)\n\n")  # Ссылка на график

    typer.echo(f"Отчёт сгенерирован в {out_root}")
if __name__ == "__main__":
    app()

