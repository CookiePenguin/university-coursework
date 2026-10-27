from pathlib import Path

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


# Пути к файлам
DATA_FILE = Path("data/v12.xlsx")
RESULTS_DIR = Path("results")
RESULTS_FILE = RESULTS_DIR / "analysis_results.xlsx"

# Названия столбцов
AREA_COLUMN = "Общая площадь, га"

CROP_COLUMNS = [
    "Зерновые и зернобобовые, га",
    "Технические, га",
    "Картофель, га",
    "Овощные и бахчевые, га",
    "Кормовые, га",
]

NUMBER_OF_GROUPS = 5
NUMBER_OF_CLUSTERS = 5


def main():
    # 1. Загружаем исходную таблицу
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Не найден исходный файл: {DATA_FILE}"
        )

    df = pd.read_excel(DATA_FILE)

    required_columns = [AREA_COLUMN, *CROP_COLUMNS]
    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"В таблице отсутствуют столбцы: {missing_columns}"
        )

    # Проверяем, что анализируемые показатели числовые
    for column in required_columns:
        df[column] = pd.to_numeric(df[column], errors="raise")

    if df[required_columns].isna().any().any():
        raise ValueError(
            "В анализируемых столбцах обнаружены пустые ячейки."
        )

    if (df[AREA_COLUMN] <= 0).any():
        raise ValueError(
            "Общая площадь должна быть положительной."
        )

    print("Исходная таблица загружена.")
    print(f"Количество организаций: {len(df)}")

    # 2. Группируем организации по общей площади
    # Ранжирование позволяет получить 5 групп даже при совпадении площадей.
    df["Группа по площади"] = (
        pd.qcut(
            df[AREA_COLUMN].rank(method="first"),
            q=NUMBER_OF_GROUPS,
            labels=False,
        ) + 1
    )

    # 3. Рассчитываем показатели для каждой группы
    grouped = df.groupby("Группа по площади", sort=True)

    group_summary = grouped.agg(
        Количество_организаций=("Организация", "count"),
        Минимальная_площадь=(AREA_COLUMN, "min"),
        Максимальная_площадь=(AREA_COLUMN, "max"),
        Средняя_площадь=(AREA_COLUMN, "mean"),
        Общая_площадь=(AREA_COLUMN, "sum"),
    )

    crop_totals = grouped[CROP_COLUMNS].sum()
    group_summary = group_summary.join(crop_totals)

    # 4. Рассчитываем структуру посевных площадей в процентах
    structure = crop_totals.div(
        group_summary["Общая_площадь"], axis=0
    ) * 100

    structure.columns = [
        f"{column} (%)" for column in CROP_COLUMNS
    ]

    structure.index.name = "Группа по площади"

    # 5. Подготавливаем данные для кластерного анализа
    # Используем доли культур, а не абсолютные площади.
    crop_shares = df[CROP_COLUMNS].div(
        df[AREA_COLUMN], axis=0
    ) * 100

    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(crop_shares)

    model = KMeans(
        n_clusters=NUMBER_OF_CLUSTERS,
        random_state=42,
        n_init=20,
    )

    df["Кластер"] = model.fit_predict(scaled_data) + 1

    # 6. Рассчитываем характеристики кластеров
    cluster_summary = df.groupby("Кластер", sort=True).agg(
        Количество_организаций=("Организация", "count"),
        Средняя_площадь=(AREA_COLUMN, "mean"),
        Общая_площадь=(AREA_COLUMN, "sum"),
    )

    cluster_crop_totals = df.groupby("Кластер")[CROP_COLUMNS].sum()
    cluster_summary = cluster_summary.join(cluster_crop_totals)

    cluster_structure = cluster_crop_totals.div(
        cluster_summary["Общая_площадь"], axis=0
    ) * 100

    cluster_structure.columns = [
        f"{column} (%)" for column in CROP_COLUMNS
    ]

    cluster_structure.index.name = "Кластер"

    # 7. Сравниваем обычную группировку и кластеры
    comparison = pd.crosstab(
        df["Группа по площади"],
        df["Кластер"],
        margins=True,
        margins_name="Всего",
    )

    comparison.index.name = "Группа по площади"

    # 8. Создаём папку для результатов
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # 9. Сохраняем результаты в отдельный Excel-файл
    with pd.ExcelWriter(RESULTS_FILE, engine="openpyxl") as writer:
        df.to_excel(
            writer,
            sheet_name="Данные и группы",
            index=False,
        )

        group_summary.to_excel(
            writer,
            sheet_name="Группировка",
        )

        structure.to_excel(
            writer,
            sheet_name="Структура посевов",
        )

        cluster_summary.to_excel(
            writer,
            sheet_name="Кластеры",
        )

        cluster_structure.to_excel(
            writer,
            sheet_name="Структура кластеров",
        )

        comparison.to_excel(
            writer,
            sheet_name="Сравнение",
        )

    # 10. Выводим краткие результаты в терминал
    print("\nГруппировка по общей площади:")
    print(
        group_summary[
            [
                "Количество_организаций",
                "Минимальная_площадь",
                "Максимальная_площадь",
                "Средняя_площадь",
            ]
        ].round(2).to_string()
    )

    print("\nКоличество организаций в кластерах:")
    print(
        df["Кластер"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print("\nСравнение группировки и кластерного анализа:")
    print(comparison.to_string())

    print(f"\nРезультаты сохранены в файл: {RESULTS_FILE}")


if __name__ == "__main__":
    main()