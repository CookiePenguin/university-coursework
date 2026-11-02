from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# ПЗ 4. РАСЧЁТ И АНАЛИЗ ПОКАЗАТЕЛЕЙ ИСПОЛЬЗОВАНИЯ
# ТРАКТОРНОГО ПАРКА
# Вариант 12
# ============================================================

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "tractor_data.csv"
RESULTS_FILE = BASE_DIR / "results.csv"
COMPARISON_FILE = BASE_DIR / "comparison.csv"
CHARTS_DIR = BASE_DIR / "charts"

GROUPS = {
    "group_i": "Группа I",
    "group_ii": "Группа II",
}

# Для условного расчёта использования календарного фонда.
# Требует сверки с методикой задачи 10.7.
DAYS_IN_YEAR = 365


# ============================================================
# 1. ЗАГРУЗКА И ПРОВЕРКА ИСХОДНЫХ ДАННЫХ
# ============================================================

def load_data() -> pd.DataFrame:
    """Загружает и проверяет исходные данные."""

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Не найден файл с исходными данными: {DATA_FILE}"
        )

    data = pd.read_csv(DATA_FILE)

    required_columns = {"indicator", "group_i", "group_ii"}

    if not required_columns.issubset(data.columns):
        raise ValueError(
            "В CSV отсутствуют необходимые столбцы: "
            "indicator, group_i, group_ii."
        )

    if data["indicator"].duplicated().any():
        raise ValueError(
            "В исходных данных обнаружены повторяющиеся показатели."
        )

    data = data.set_index("indicator")

    required_indicators = {
        "physical_tractors",
        "serviceable_tractors",
        "reference_tractors",
        "reference_machine_shifts",
        "reference_machine_days",
        "transport_machine_days",
        "completed_standard_shifts",
        "total_work_thousand_reference_ha",
        "transport_work_thousand_reference_ha",
        "tractor_drivers",
        "qualified_drivers",
        "arable_land_thousand_ha",
        "tractor_book_value_million_rub",
        "agricultural_machinery_book_value_million_rub",
    }

    missing_indicators = required_indicators - set(data.index)

    if missing_indicators:
        raise ValueError(
            "В исходных данных отсутствуют показатели: "
            + ", ".join(sorted(missing_indicators))
        )

    data = data.loc[sorted(required_indicators)].copy()

    if data[list(GROUPS)].isna().any().any():
        raise ValueError(
            "В исходных данных обнаружены пропущенные значения."
        )

    try:
        data[list(GROUPS)] = data[list(GROUPS)].apply(
            pd.to_numeric,
            errors="raise"
        )
    except (ValueError, TypeError) as error:
        raise ValueError(
            "В исходных данных обнаружены нечисловые значения."
        ) from error

    if (data[list(GROUPS)] < 0).any().any():
        raise ValueError(
            "В исходных данных обнаружены отрицательные значения."
        )

    # Проверка положительных знаменателей.
    positive_indicators = [
        "physical_tractors",
        "reference_tractors",
        "reference_machine_shifts",
        "reference_machine_days",
        "tractor_drivers",
        "arable_land_thousand_ha",
    ]

    for indicator in positive_indicators:
        if (data.loc[indicator, list(GROUPS)] <= 0).any():
            raise ValueError(
                f"Показатель «{indicator}» должен быть больше нуля."
            )

    # Проверка логических соотношений исходных данных.
    for group in GROUPS:

        physical = data.loc["physical_tractors", group]
        serviceable = data.loc["serviceable_tractors", group]

        drivers = data.loc["tractor_drivers", group]
        qualified = data.loc["qualified_drivers", group]

        machine_days = data.loc["reference_machine_days", group]
        transport_days = data.loc["transport_machine_days", group]

        total_work = data.loc[
            "total_work_thousand_reference_ha", group
        ]
        transport_work = data.loc[
            "transport_work_thousand_reference_ha", group
        ]

        if serviceable > physical:
            raise ValueError(
                f"{GROUPS[group]}: исправных тракторов больше, "
                "чем физических тракторов."
            )

        if qualified > drivers:
            raise ValueError(
                f"{GROUPS[group]}: трактористов I и II класса больше, "
                "чем всех трактористов."
            )

        if transport_days > machine_days:
            raise ValueError(
                f"{GROUPS[group]}: транспортных машино-дней больше, "
                "чем всех машино-дней."
            )

        if transport_work > total_work:
            raise ValueError(
                f"{GROUPS[group]}: объём транспортных работ больше "
                "общего объёма работ."
            )

    print("Исходные данные успешно загружены и проверены.")

    return data


# ============================================================
# 2. РАСЧЁТ ПОКАЗАТЕЛЕЙ
# ============================================================

def calculate_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """Рассчитывает систему показателей тракторного парка."""

    results = {}

    for group in GROUPS:

        physical = data.loc["physical_tractors", group]
        serviceable = data.loc["serviceable_tractors", group]
        reference = data.loc["reference_tractors", group]

        machine_shifts = data.loc[
            "reference_machine_shifts", group
        ]
        machine_days = data.loc[
            "reference_machine_days", group
        ]
        transport_days = data.loc[
            "transport_machine_days", group
        ]
        standard_shifts = data.loc[
            "completed_standard_shifts", group
        ]

        total_work = data.loc[
            "total_work_thousand_reference_ha", group
        ]
        transport_work = data.loc[
            "transport_work_thousand_reference_ha", group
        ]

        drivers = data.loc["tractor_drivers", group]
        qualified_drivers = data.loc[
            "qualified_drivers", group
        ]

        arable_land = data.loc[
            "arable_land_thousand_ha", group
        ]

        tractor_value = data.loc[
            "tractor_book_value_million_rub", group
        ]
        machinery_value = data.loc[
            "agricultural_machinery_book_value_million_rub", group
        ]

        results[group] = {

            # Техническое состояние

            "Коэффициент технической исправности, %":
                serviceable / physical * 100,

            "Коэффициент перевода физических тракторов в эталонные":
                reference / physical,

            # Обеспеченность техникой

            "Эталонные тракторы на 1000 га пашни":
                reference / arable_land,

            "Нагрузка пашни на один эталонный трактор, га":
                arable_land * 1000 / reference,

            # Использование тракторного парка

            "Машино-дни на один эталонный трактор":
                machine_days / reference,

            "Использование календарного фонда времени, %":
                machine_days / reference / DAYS_IN_YEAR * 100,

            "Коэффициент сменности":
                machine_shifts / machine_days,

            "Выполнение нормосмен на одну машино-смену":
                standard_shifts / machine_shifts,

            # Производительность

            "Годовая выработка на эталонный трактор, эт. га":
                total_work * 1000 / reference,

            "Выработка на один машино-день, эт. га":
                total_work * 1000 / machine_days,

            "Выработка на одну машино-смену, эт. га":
                total_work * 1000 / machine_shifts,

            # Транспортные работы

            "Доля транспортных работ в объёме, %":
                transport_work / total_work * 100,

            "Доля транспортных машино-дней, %":
                transport_days / machine_days * 100,

            # Трудовые ресурсы

            "Трактористов на один физический трактор":
                drivers / physical,

            "Доля трактористов I и II класса, %":
                qualified_drivers / drivers * 100,

            "Выработка на одного тракториста, эт. га":
                total_work * 1000 / drivers,

            # Стоимость техники

            "Балансовая стоимость тракторов на эталонный трактор, млн руб.":
                tractor_value / reference,

            "Балансовая стоимость сельхозмашин на эталонный трактор, млн руб.":
                machinery_value / reference,

            "Совокупная стоимость техники на эталонный трактор, млн руб.":
                (tractor_value + machinery_value) / reference,
        }

    return pd.DataFrame(results)


# ============================================================
# 3. ФОРМИРОВАНИЕ СРАВНИТЕЛЬНОЙ ТАБЛИЦЫ
# ============================================================

def create_comparison(
    indicators: pd.DataFrame
) -> pd.DataFrame:
    """
    Формирует сравнение групп I и II.

    Разница рассчитывается как II - I.
    Отношение рассчитывается как II / I * 100%.
    """

    comparison = pd.DataFrame(index=indicators.index)

    comparison["Группа I"] = indicators["group_i"]
    comparison["Группа II"] = indicators["group_ii"]

    comparison["Разница II - I"] = (
        indicators["group_ii"] - indicators["group_i"]
    )

    comparison["Отношение II к I, %"] = (
        indicators["group_ii"] / indicators["group_i"] * 100
    )

    return comparison


# ============================================================
# 4. СОХРАНЕНИЕ РЕЗУЛЬТАТОВ
# ============================================================

def save_results(
    indicators: pd.DataFrame,
    comparison: pd.DataFrame
) -> None:
    """Сохраняет расчётную и сравнительную таблицы."""

    indicators.round(2).to_csv(
        RESULTS_FILE,
        encoding="utf-8-sig"
    )

    comparison.round(2).to_csv(
        COMPARISON_FILE,
        encoding="utf-8-sig"
    )

    print(f"\nРасчётная таблица сохранена: {RESULTS_FILE.name}")
    print(f"Сравнительная таблица сохранена: {COMPARISON_FILE.name}")


# ============================================================
# 5. ПОСТРОЕНИЕ ГРАФИКОВ
# ============================================================

def create_charts(indicators: pd.DataFrame) -> None:
    """Строит графики сравнения двух групп предприятий."""

    CHARTS_DIR.mkdir(exist_ok=True)

    charts = {
        "technical_condition.png": (
            "Коэффициент технической исправности, %",
            "Техническая исправность тракторов",
        ),

        "tractor_supply.png": (
            "Эталонные тракторы на 1000 га пашни",
            "Обеспеченность пашни эталонными тракторами",
        ),

        "productivity.png": (
            "Годовая выработка на эталонный трактор, эт. га",
            "Годовая производительность тракторов",
        ),

        "transport_work.png": (
            "Доля транспортных работ в объёме, %",
            "Доля транспортных работ",
        ),

        "qualified_drivers.png": (
            "Доля трактористов I и II класса, %",
            "Квалификация трактористов",
        ),
    }

    CHARTS_DIR.mkdir(exist_ok=True)

    for filename, (indicator, title) in charts.items():

        values = indicators.loc[indicator]
        labels = [GROUPS[group] for group in values.index]

        plt.figure(figsize=(9, 5))

        bars = plt.bar(labels, values.values)

        plt.title(title)
        plt.ylabel(indicator)
        plt.xlabel("Группы предприятий")
        plt.grid(axis="y", alpha=0.3)

        for bar, value in zip(bars, values.values):
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                f"{value:.2f}",
                ha="center",
                va="bottom",
            )

        plt.tight_layout()
        plt.savefig(CHARTS_DIR / filename, dpi=150)
        plt.close()

    print(f"Графики сохранены в папке: {CHARTS_DIR.name}")


# ============================================================
# 6. ВЫВОД СРАВНИТЕЛЬНОЙ ТАБЛИЦЫ
# ============================================================

def print_comparison(comparison: pd.DataFrame) -> None:
    """Выводит полную сравнительную таблицу."""

    print("\n" + "=" * 110)
    print("СРАВНИТЕЛЬНАЯ ТАБЛИЦА ПОКАЗАТЕЛЕЙ")
    print("=" * 110)

    print(
        comparison.round(2).to_string(
            formatters={
                "Группа I": "{:.2f}".format,
                "Группа II": "{:.2f}".format,
                "Разница II - I": "{:+.2f}".format,
                "Отношение II к I, %": "{:.2f}".format,
            }
        )
    )
    print("\nПояснения:")
    print("Разница II - I = значение группы II минус значение группы I.")
    print("Отношение II к I = значение группы II / значение группы I × 100%.")
    print(
    "Для процентных показателей разница выражается в процентных пунктах."
    )
    print(
    "Все сравнительные показатели рассчитаны по неокруглённым значениям; "
    "округление выполнено только при отображении результатов."
    )

# ============================================================
# 7. АНАЛИЗ И ВЫВОДЫ
# ============================================================

def print_analysis(indicators: pd.DataFrame) -> None:
    """Формирует содержательные выводы по результатам сравнения."""

    print("\n" + "=" * 75)
    print("АНАЛИЗ ИСПОЛЬЗОВАНИЯ ТРАКТОРНОГО ПАРКА")
    print("=" * 75)

    # Техническое состояние
    first = indicators.loc[
        "Коэффициент технической исправности, %", "group_i"
    ]
    second = indicators.loc[
        "Коэффициент технической исправности, %", "group_ii"
    ]

    print("\n1. Техническое состояние тракторного парка.")

    print(
        f"В группе I техническая исправность составляет {first:.2f}%, "
        f"в группе II — {second:.2f}%."
    )

    if first > second:
        print(
            f"В группе I доля исправных тракторов выше на "
            f"{first - second:.2f} процентного пункта."
        )
    elif second > first:
        print(
            f"В группе II доля исправных тракторов выше на "
            f"{second - first:.2f} процентного пункта."
        )
    else:
        print("Доля исправных тракторов в группах одинакова.")

    # Обеспеченность техникой
    first = indicators.loc[
        "Эталонные тракторы на 1000 га пашни", "group_i"
    ]
    second = indicators.loc[
        "Эталонные тракторы на 1000 га пашни", "group_ii"
    ]

    print("\n2. Обеспеченность пашни эталонными тракторами.")

    print(
        f"На 1000 га пашни приходится {first:.2f} эталонного трактора "
        f"в группе I и {second:.2f} — в группе II."
    )

    if second > first:
        print("Относительная обеспеченность пашни тракторами выше в группе II.")
    else:
        print("Относительная обеспеченность пашни тракторами выше в группе I.")

    # Годовая производительность
    first = indicators.loc[
        "Годовая выработка на эталонный трактор, эт. га", "group_i"
    ]
    second = indicators.loc[
        "Годовая выработка на эталонный трактор, эт. га", "group_ii"
    ]

    print("\n3. Годовая производительность тракторов.")

    print(
        f"Годовая выработка на один эталонный трактор составляет "
        f"{first:.2f} эт. га в группе I и {second:.2f} эт. га в группе II."
    )

    if first > second:
        print(
            "В группе I годовая выработка на один эталонный трактор выше."
        )
    elif second > first:
        print(
            "В группе II годовая выработка на один эталонный трактор выше."
        )
    else:
        print("Годовая выработка в группах одинакова.")

    # Транспортные работы
    first = indicators.loc[
        "Доля транспортных работ в объёме, %", "group_i"
    ]
    second = indicators.loc[
        "Доля транспортных работ в объёме, %", "group_ii"
    ]

    print("\n4. Структура выполненных работ.")

    print(
        f"Доля транспортных работ составляет {first:.2f}% "
        f"в группе I и {second:.2f}% в группе II."
    )

    print(
        "Этот показатель характеризует структуру работ, "
        "а не эффективность тракторного парка сам по себе."
    )

    # Квалификация трактористов
    first = indicators.loc[
        "Доля трактористов I и II класса, %", "group_i"
    ]
    second = indicators.loc[
        "Доля трактористов I и II класса, %", "group_ii"
    ]

    print("\n5. Квалификация трактористов.")

    print(
        f"Доля трактористов I и II класса составляет {first:.2f}% "
        f"в группе I и {second:.2f}% в группе II."
    )

    if second > first:
        print(
            "В группе II выше доля трактористов I и II класса."
        )
    elif first > second:
        print(
            "В группе I выше доля трактористов I и II класса."
        )
    else:
        print("Доли квалифицированных трактористов одинаковы.")

    # Коэффициент сменности
    first = indicators.loc["Коэффициент сменности", "group_i"]
    second = indicators.loc["Коэффициент сменности", "group_ii"]

    print("\n6. Использование тракторов в течение рабочего дня.")

    print(f"Коэффициент сменности группы I: {first:.2f}.")
    print(f"Коэффициент сменности группы II: {second:.2f}.")

    if second < 1:
        print(
            "Во второй группе коэффициент сменности меньше единицы. "
            "Необходимо проверить исходную методику учёта машино-смен "
            "и машино-дней. Исходные данные не корректировались."
        )

    # Итог
    print("\n" + "=" * 75)
    print("ОБЩИЙ ВЫВОД")
    print("=" * 75)

    print(
        "Сравнение показывает различия между группами предприятий "
        "по техническому состоянию тракторов, обеспеченности техникой, "
        "производительности, структуре работ и квалификации трактористов."
    )

    print(
        "В группе I выше коэффициент технической исправности и годовая "
        "выработка на один эталонный трактор."
    )

    print(
        "В группе II выше обеспеченность пашни эталонными тракторами "
        "и доля трактористов I и II класса. Также в этой группе выше "
        "доля транспортных работ в общем объёме."
    )

    print(
        "По совокупности показателей нельзя однозначно объявить одну "
        "группу более эффективной: результаты характеризуют разные "
        "стороны использования тракторного парка."
    )

    print(
        "\nПримечание: использование календарного фонда рассчитано "
        f"условно исходя из {DAYS_IN_YEAR} календарных дней. "
        "Формулу необходимо сверить с задачей 10.7 практикума."
    )

    print(
        "\nСравнение выполнено между двумя группами предприятий, "
        "а не между временными периодами."
    )


# ============================================================
# 8. ГЛАВНАЯ ФУНКЦИЯ
# ============================================================

def main():

    print("=" * 75)
    print("ПЗ 4. РАСЧЁТ И АНАЛИЗ ПОКАЗАТЕЛЕЙ ИСПОЛЬЗОВАНИЯ")
    print("ТРАКТОРНОГО ПАРКА")
    print("Вариант 12")
    print("=" * 75)

    # Загрузка данных
    data = load_data()

    print("\nИСХОДНЫЕ ДАННЫЕ:")
    print(data.to_string())

    print(f"\nКоличество исходных показателей: {len(data)}")

    # Расчёт показателей
    indicators = calculate_indicators(data)

    print("\n" + "=" * 75)
    print("РАССЧИТАННЫЕ ПОКАЗАТЕЛИ")
    print("=" * 75)

    print(indicators.round(2).to_string())

    # Формирование сравнительной таблицы
    comparison = create_comparison(indicators)

    # Сохранение таблиц
    save_results(indicators, comparison)

    # Построение графиков
    create_charts(indicators)

    # Полная сравнительная таблица
    print_comparison(comparison)

    # Анализ и выводы
    print_analysis(indicators)

    print("\n" + "=" * 75)
    print("РАБОТА ПРОГРАММЫ ЗАВЕРШЕНА УСПЕШНО")
    print("=" * 75)


if __name__ == "__main__":
    main()