from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# ПЗ 4. РАСЧЁТ И АНАЛИЗ ПОКАЗАТЕЛЕЙ ИСПОЛЬЗОВАНИЯ ТРАКТОРНОГО
# ПАРКА
# Вариант 12
# ============================================================

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "tractor_data.csv"
RESULTS_FILE = BASE_DIR / "results.csv"
CHARTS_DIR = BASE_DIR / "charts"

GROUPS = {
    "group_i": "Группа I",
    "group_ii": "Группа II",
}


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
        raise ValueError("В CSV отсутствуют необходимые столбцы.")

    if data["indicator"].duplicated().any():
        raise ValueError("В исходных данных обнаружены повторяющиеся показатели.")

    data = data.set_index("indicator")

    if data.isna().any().any():
        raise ValueError("В исходных данных обнаружены пропущенные значения.")

    if not all(group in data.columns for group in GROUPS):
        raise ValueError("Не найдены столбцы обеих групп предприятий.")

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

        machine_shifts = data.loc["reference_machine_shifts", group]
        machine_days = data.loc["reference_machine_days", group]
        transport_days = data.loc["transport_machine_days", group]
        standard_shifts = data.loc["completed_standard_shifts", group]

        total_work = data.loc["total_work_thousand_reference_ha", group]
        transport_work = data.loc["transport_work_thousand_reference_ha", group]

        drivers = data.loc["tractor_drivers", group]
        qualified_drivers = data.loc["qualified_drivers", group]

        arable_land = data.loc["arable_land_thousand_ha", group]

        tractor_value = data.loc["tractor_book_value_million_rub", group]
        machinery_value = data.loc[
            "agricultural_machinery_book_value_million_rub", group
        ]

        results[group] = {

            # Техническое состояние тракторного парка

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
                machine_days / reference / 365 * 100,

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
# 3. СОХРАНЕНИЕ РЕЗУЛЬТАТОВ
# ============================================================

def save_results(indicators: pd.DataFrame) -> None:
    """Сохраняет рассчитанные показатели в CSV."""

    indicators.round(2).to_csv(
        RESULTS_FILE,
        encoding="utf-8-sig"
    )

    print(f"\nТаблица результатов сохранена: {RESULTS_FILE.name}")


# ============================================================
# 4. ПОСТРОЕНИЕ ГРАФИКОВ
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

    for filename, (indicator, title) in charts.items():

        values = indicators.loc[indicator]
        labels = [GROUPS[group] for group in values.index]

        plt.figure(figsize=(9, 5))

        bars = plt.bar(labels, values.values)

        plt.title(title)
        plt.ylabel(indicator)
        plt.xlabel("Группы предприятий")
        plt.grid(axis="y", alpha=0.3)

        # Подписи значений над столбцами
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
# 5. ФОРМИРОВАНИЕ СРАВНИТЕЛЬНОГО АНАЛИЗА
# ============================================================

def print_analysis(indicators: pd.DataFrame) -> None:
    """Выводит сравнительный анализ результатов."""

    print("\n" + "=" * 65)
    print("СРАВНИТЕЛЬНЫЙ АНАЛИЗ ГРУПП ПРЕДПРИЯТИЙ")
    print("=" * 65)

    comparisons = [
        (
            "Коэффициент технической исправности, %",
            "Техническая исправность тракторов",
            "%",
        ),
        (
            "Эталонные тракторы на 1000 га пашни",
            "Обеспеченность пашни эталонными тракторами",
            "",
        ),
        (
            "Годовая выработка на эталонный трактор, эт. га",
            "Годовая выработка на эталонный трактор",
            " эт. га",
        ),
        (
            "Доля транспортных работ в объёме, %",
            "Доля транспортных работ",
            "%",
        ),
        (
            "Доля трактористов I и II класса, %",
            "Доля квалифицированных трактористов",
            "%",
        ),
    ]

    for indicator, description, unit in comparisons:

        first = indicators.loc[indicator, "group_i"]
        second = indicators.loc[indicator, "group_ii"]

        print(f"\n{description}:")
        print(f"  Группа I:  {first:.2f}{unit}")
        print(f"  Группа II: {second:.2f}{unit}")

        if first > second:
            print("  Более высокое значение наблюдается в группе I.")
        elif second > first:
            print("  Более высокое значение наблюдается в группе II.")
        else:
            print("  Значения в группах одинаковые.")

    print("\nОсобенность коэффициента сменности:")

    for group, label in GROUPS.items():
        value = indicators.loc["Коэффициент сменности", group]

        print(f"  {label}: {value:.2f}")

    print(
        "\nКоэффициент сменности группы II меньше единицы. "
        "Это требует проверки исходной методики учёта машино-смен "
        "и машино-дней. Исходные значения при этом не изменялись."
    )

    print(
        "\nСравнение выполнено между двумя группами предприятий, "
        "а не между временными периодами."
    )


# ============================================================
# 6. ГЛАВНАЯ ФУНКЦИЯ
# ============================================================

def main():

    print("=" * 65)
    print("ПЗ 4. РАСЧЁТ И АНАЛИЗ ПОКАЗАТЕЛЕЙ ИСПОЛЬЗОВАНИЯ")
    print("ТРАКТОРНОГО ПАРКА")
    print("Вариант 12")
    print("=" * 65)

    # Загрузка данных
    data = load_data()

    print("\nИСХОДНЫЕ ДАННЫЕ:")
    print(data.to_string())

    print(f"\nКоличество показателей: {len(data)}")
    print(f"Количество пропусков: {data.isna().sum().sum()}")

    # Расчёт показателей
    indicators = calculate_indicators(data)

    print("\n" + "=" * 65)
    print("РАССЧИТАННЫЕ ПОКАЗАТЕЛИ")
    print("=" * 65)

    print(indicators.round(2).to_string())

    # Сохранение результатов
    save_results(indicators)

    # Создание графиков
    create_charts(indicators)

    # Сравнительный анализ
    print_analysis(indicators)

    print("\n" + "=" * 65)
    print("РАБОТА ПРОГРАММЫ ЗАВЕРШЕНА УСПЕШНО")
    print("=" * 65)


if __name__ == "__main__":
    main()
