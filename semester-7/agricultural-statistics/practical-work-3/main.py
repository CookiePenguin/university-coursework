from calendar import monthrange
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


# ============================================================
# 1. Исходные данные — практическая работа № 3, вариант 12
# ============================================================

YEAR = 2025

MONTHS = [
    "Январь",
    "Февраль",
    "Март",
    "Апрель",
    "Май",
    "Июнь",
    "Июль",
    "Август",
    "Сентябрь",
    "Октябрь",
    "Ноябрь",
    "Декабрь",
]

POPULATION = [
    3207,
    2785,
    3278,
    3487,
    5198,
    8133,
    8658,
    8933,
    10101,
    8687,
    6495,
    4265,
]

# Папка для результатов
RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)


def main():
    # ========================================================
    # 2. Подготовка исходной таблицы
    # ========================================================

    data = pd.DataFrame({
        "Месяц": MONTHS,
        "Поголовье, голов": POPULATION,
    })

    print("=" * 60)
    print("ПРАКТИЧЕСКАЯ РАБОТА № 3")
    print("Определение средней численности животных")
    print("Вариант 12")
    print("=" * 60)

    print("\n1. Исходные данные:")
    print(data.to_string(index=False))

    # ========================================================
    # 3. Средняя арифметическая исходных значений
    # ========================================================

    arithmetic_mean = sum(POPULATION) / len(POPULATION)

    print("\n2. Средняя арифметическая 12 значений:")
    print(f"{arithmetic_mean:.2f} голов")

    # ========================================================
    # 4. Средняя хронологическая с учётом длительности
    #    интервалов между наблюдениями
    # ========================================================
    #
    # Предположение: значения относятся к началу каждого
    # месяца, а изменение между соседними наблюдениями
    # считается линейным.
    #
    # Рассматриваем период с 1 января по 1 декабря.
    # Поэтому учитываем интервалы от января до февраля,
    # от февраля до марта и так далее до ноября-декабря.
    # ========================================================

    intervals = []

    weighted_sum = 0
    total_days = 0

    for i in range(len(POPULATION) - 1):
        month_number = i + 1

        days = monthrange(YEAR, month_number)[1]

        current_population = POPULATION[i]
        next_population = POPULATION[i + 1]

        interval_average = (
            current_population + next_population
        ) / 2

        weighted_value = interval_average * days

        intervals.append({
            "Начало интервала": MONTHS[i],
            "Конец интервала": MONTHS[i + 1],
            "Длительность, дней": days,
            "Поголовье в начале": current_population,
            "Поголовье в конце": next_population,
            "Среднее за интервал": interval_average,
            "Взвешенное значение": weighted_value,
        })

        weighted_sum += weighted_value
        total_days += days

    chronological_mean = weighted_sum / total_days

    intervals_df = pd.DataFrame(intervals)

    print("\n3. Расчёт средней хронологической:")
    print(intervals_df.to_string(
        index=False,
        formatters={
            "Среднее за интервал": "{:.2f}".format,
            "Взвешенное значение": "{:.2f}".format,
        },
    ))

    print(f"\nОбщая продолжительность: {total_days} дней")
    print(f"Сумма взвешенных значений: {weighted_sum:.2f}")
    print(
        "Средняя хронологическая: "
        f"{chronological_mean:.2f} голов"
    )

    # ========================================================
    # 5. Изменение поголовья по месяцам
    # ========================================================

    data["Изменение к предыдущему месяцу"] = (
        data["Поголовье, голов"].diff()
    )

    data["Изменение, %"] = (
        data["Поголовье, голов"].pct_change() * 100
    )

    print("\n4. Изменение поголовья:")
    print(data.to_string(
        index=False,
        formatters={
            "Изменение, %": (
                lambda value: (
                    "-" if pd.isna(value) else f"{value:.2f}"
                )
            ),
        },
    ))

    # ========================================================
    # 6. Столбчатая диаграмма
    # ========================================================

    plt.figure(figsize=(12, 6))

    bars = plt.bar(
        MONTHS,
        POPULATION,
        edgecolor="black",
    )

    plt.title(
        "Динамика поголовья свиней по месяцам\n"
        "Вариант 12",
        fontsize=14,
    )

    plt.xlabel("Месяц")
    plt.ylabel("Поголовье, голов")

    plt.xticks(rotation=35, ha="right")
    plt.grid(axis="y", linestyle="--", alpha=0.5)

    # Подписываем каждый столбец числовым значением
    plt.bar_label(bars, fmt="%.0f", padding=3)

    plt.tight_layout()

    chart_path = RESULTS_DIR / "pig_population_by_month.png"
    plt.savefig(chart_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"\nСтолбчатая диаграмма сохранена: {chart_path}")

    # ========================================================
    # 7. Предварительные выводы
    # ========================================================

    maximum_index = POPULATION.index(max(POPULATION))
    minimum_index = POPULATION.index(min(POPULATION))

    print("\n5. Предварительные выводы:")
    print(
        f"Максимальное поголовье: {max(POPULATION)} голов "
        f"({MONTHS[maximum_index]})."
    )
    print(
        f"Минимальное поголовье: {min(POPULATION)} голов "
        f"({MONTHS[minimum_index]})."
    )
    print(
        "Средняя арифметическая за 12 месяцев: "
        f"{arithmetic_mean:.2f} голов."
    )
    print(
        "Средняя хронологическая за рассматриваемый период: "
        f"{chronological_mean:.2f} голов."
    )

    print(
        "\nВажно: средняя хронологическая рассчитана "
        "при предположении о моментных наблюдениях "
        "на начало каждого месяца и линейном изменении "
        "между ними."
    )
    # ========================================================
    # 8. Анализ динамики и сезонной компоненты
    # ========================================================

    data["Скользящее среднее за 3 месяца"] = (
        data["Поголовье, голов"]
        .rolling(window=3, center=True)
        .mean()
    )

    print("\n6. Трёхмесячное скользящее среднее:")
    print(
        data[
            [
                "Месяц",
                "Поголовье, голов",
                "Скользящее среднее за 3 месяца",
            ]
        ].to_string(
            index=False,
            formatters={
                "Скользящее среднее за 3 месяца": (
                    lambda value: (
                        "-" if pd.isna(value) else f"{value:.2f}"
                    )
                ),
            },
        )
    )

    # График динамики и скользящего среднего
    plt.figure(figsize=(12, 6))

    plt.plot(
        MONTHS,
        POPULATION,
        marker="o",
        label="Фактическое поголовье",
    )

    plt.plot(
        MONTHS,
        data["Скользящее среднее за 3 месяца"],
        marker="s",
        linestyle="--",
        label="Скользящее среднее за 3 месяца",
    )

    plt.title(
        "Динамика поголовья свиней и скользящее среднее\n"
        "Вариант 12",
        fontsize=14,
    )

    plt.xlabel("Месяц")
    plt.ylabel("Поголовье, голов")
    plt.xticks(rotation=35, ha="right")
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()

    moving_average_path = RESULTS_DIR / "moving_average.png"

    plt.savefig(
        moving_average_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    print(
        "\nГрафик скользящего среднего сохранён: "
        f"{moving_average_path}"
    )

    # Предварительная оценка сезонности
    print("\n7. Анализ сезонной компоненты:")
    print(
        "В течение года наблюдается рост поголовья "
        "к лету и началу осени, а затем снижение."
    )
    print(
        "По одному году наблюдений нельзя надёжно "
        "подтвердить повторяющуюся сезонную компоненту."
    )
    print(
        "Для проверки сезонности необходимы данные "
        "за несколько лет и сравнение одноимённых месяцев."
    )
        # ========================================================
    # 9. Экспорт результатов в Excel
    # ========================================================

    # Подготавливаем итоговые показатели
    conclusions_df = pd.DataFrame({
        "Показатель": [
            "Вариант",
            "Количество наблюдений",
            "Средняя арифметическая, голов",
            "Средняя хронологическая, голов",
            "Общая продолжительность интервалов, дней",
            "Минимальное поголовье, голов",
            "Месяц минимального поголовья",
            "Максимальное поголовье, голов",
            "Месяц максимального поголовья",
            "Вывод о сезонности",
            "Допущение при расчёте средней хронологической",
        ],
        "Значение": [
            12,
            len(POPULATION),
            arithmetic_mean,
            chronological_mean,
            total_days,
            min(POPULATION),
            MONTHS[minimum_index],
            max(POPULATION),
            MONTHS[maximum_index],
            (
                "По одному году нельзя надёжно подтвердить "
                "повторяющуюся сезонность"
            ),
            (
                "Наблюдения считаются моментными на начало "
                "месяца; между ними предполагается "
                "линейное изменение"
            ),
        ],
    })

    # Сохраняем четыре листа в один Excel-файл
    excel_path = RESULTS_DIR / "analysis_results.xlsx"

    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        data.to_excel(
            writer,
            sheet_name="Исходные данные",
            index=False,
        )

        intervals_df.to_excel(
            writer,
            sheet_name="Расчёт средней",
            index=False,
        )

        data[
            [
                "Месяц",
                "Поголовье, голов",
                "Изменение к предыдущему месяцу",
                "Изменение, %",
                "Скользящее среднее за 3 месяца",
            ]
        ].to_excel(
            writer,
            sheet_name="Динамика",
            index=False,
        )

        conclusions_df.to_excel(
            writer,
            sheet_name="Выводы",
            index=False,
        )

    # ========================================================
    # 9. Экспорт результатов в Excel
    # ========================================================

    conclusions_df = pd.DataFrame({
        "Показатель": [
            "Вариант",
            "Количество наблюдений",
            "Средняя арифметическая, голов",
            "Средняя хронологическая, голов",
            "Общая продолжительность интервалов, дней",
            "Минимальное поголовье, голов",
            "Месяц минимального поголовья",
            "Максимальное поголовье, голов",
            "Месяц максимального поголовья",
            "Вывод о сезонности",
            "Допущение при расчёте средней хронологической",
        ],
        "Значение": [
            12,
            len(POPULATION),
            arithmetic_mean,
            chronological_mean,
            total_days,
            min(POPULATION),
            MONTHS[POPULATION.index(min(POPULATION))],
            max(POPULATION),
            MONTHS[POPULATION.index(max(POPULATION))],
            (
                "По одному году нельзя надёжно подтвердить "
                "повторяющуюся сезонность"
            ),
            (
                "Наблюдения считаются моментными на начало "
                "месяца; между ними предполагается "
                "линейное изменение"
            ),
        ],
    })

    excel_path = RESULTS_DIR / "analysis_results.xlsx"

    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        data.to_excel(
            writer,
            sheet_name="Исходные данные",
            index=False,
        )

        intervals_df.to_excel(
            writer,
            sheet_name="Расчёт средней",
            index=False,
        )

        data[
            [
                "Месяц",
                "Поголовье, голов",
                "Изменение к предыдущему месяцу",
                "Изменение, %",
                "Скользящее среднее за 3 месяца",
            ]
        ].to_excel(
            writer,
            sheet_name="Динамика",
            index=False,
        )

        conclusions_df.to_excel(
            writer,
            sheet_name="Выводы",
            index=False,
        )

    print(f"\nExcel-файл сохранён: {excel_path}")

    print("\nПервый этап расчётов завершён.")


if __name__ == "__main__":
    main()