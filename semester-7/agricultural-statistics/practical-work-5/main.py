"""ПЗ 5. Расчёт показателей наличия и занятости трудовых ресурсов. Вариант 12."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter

plt.switch_backend("Agg")

VARIANT = 12
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / f"variant{VARIANT}.csv"
CHARTS_DIR = BASE_DIR / "charts"

# Номера строк исходного листа (как в методических материалах ПЗ 5)
ROW_POPULATION = 2   # постоянное население
ROW_A = 4            # население в трудоспособном возрасте
ROW_PENSION_POP = 5  # население пенсионного возраста до 72 лет (справочно)
ROW_I = 6            # неработающие инвалиды I/II групп и льготные пенсионеры
ROW_E = 8            # занятые в экономике, всего
ROW_P = 10           # работающие пенсионеры
ROW_M = 11           # работающие подростки 15 лет и старше
ROW_U = 12           # безработные, всего
ROW_U_PENSION = 13   # безработные пенсионного возраста
ROW_R = 14           # зарегистрированные безработные

PERCENT_KEYS = {
    "Уровень безработицы, %",
    "Зарегистрированные / все безработные, %",
    "Занятые / трудовые ресурсы, %",
    "Занятые / рабочая сила, %",
    "Трудовые ресурсы / население, %",
    "Зарегистрированные / рабочая сила, %",
    "Рабочая сила / трудовые ресурсы, %",
    "Работающие трудоспособного возраста, %",
}

BEGIN_COLOR = "#2aa198"
END_COLOR = "#d4a017"
ZOOM_NOTE = "Ось Y не начинается с нуля: масштаб увеличен для наглядности различий"


def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Не найден файл исходных данных: {path}")
    frame = pd.read_csv(path)
    if frame.shape[1] < 3:
        raise ValueError("Ожидаются три колонки: показатель, начало, конец")
    if frame.shape[0] < 13:
        raise ValueError("Нарушена структура строк исходного листа")
    return frame


def value(df: pd.DataFrame, excel_row: int, col: int) -> float:
    number = pd.to_numeric(df.iloc[excel_row - 2, col], errors="coerce")
    if pd.isna(number) or number < 0:
        raise ValueError(f"Некорректное значение в строке {excel_row}, колонке {col}")
    return float(number)


def check_logic(df: pd.DataFrame, col: int) -> None:
    population = value(df, ROW_POPULATION, col)
    a = value(df, ROW_A, col)
    i = value(df, ROW_I, col)
    e = value(df, ROW_E, col)
    p = value(df, ROW_P, col)
    m = value(df, ROW_M, col)
    u = value(df, ROW_U, col)
    u_pension = value(df, ROW_U_PENSION, col)
    r = value(df, ROW_R, col)

    checks = [
        (a <= population, "трудоспособное население больше всего населения"),
        (i <= a, "исключаемые категории больше трудоспособного населения"),
        (p + m <= e, "работающие пенсионеры и подростки больше всех занятых"),
        (u_pension <= u, "безработные пенсионеры больше всех безработных"),
        (r <= u, "зарегистрированных больше, чем всех безработных"),
        (e + u <= population, "рабочая сила больше постоянного населения"),
        (e + u > 0, "нулевая рабочая сила: деление невозможно"),
        (u > 0, "нулевое число безработных: деление невозможно"),
    ]
    for condition, message in checks:
        if not condition:
            raise ValueError(f"Нарушено логическое ограничение: {message}")


def calc(df: pd.DataFrame, col: int) -> dict:
    population = value(df, ROW_POPULATION, col)
    a = value(df, ROW_A, col)
    i = value(df, ROW_I, col)
    e = value(df, ROW_E, col)
    p = value(df, ROW_P, col)
    m = value(df, ROW_M, col)
    u = value(df, ROW_U, col)
    u_pension = value(df, ROW_U_PENSION, col)
    r = value(df, ROW_R, col)

    resources = a - i + p + m          # T = A - I + P + M
    workforce = e + u                  # L = E + U
    employed_working_age = e - p - m
    able_bodied = a - i

    return {
        "Постоянное население": population,
        "Население в трудоспособном возрасте": a,
        "Неработающие инвалиды и льготные пенсионеры": i,
        "Занятые, всего": e,
        "Занятые пенсионного возраста": p,
        "Работающие подростки": m,
        "Безработные, всего": u,
        "Зарегистрированные безработные": r,
        "Трудовые ресурсы (учебн.)": resources,
        "Рабочая сила": workforce,
        "Занятые в трудоспособном возрасте": employed_working_age,
        "Безработные вне пенсионного возраста": u - u_pension,
        "Уровень безработицы, %": u / workforce * 100,
        "Зарегистрированные / все безработные, %": r / u * 100,
        "Занятые / трудовые ресурсы, %": e / resources * 100,
        "Занятые / рабочая сила, %": e / workforce * 100,
        "Трудовые ресурсы / население, %": resources / population * 100,
        "Зарегистрированные / рабочая сила, %": r / workforce * 100,
        "Рабочая сила / трудовые ресурсы, %": workforce / resources * 100,
        "Работающие трудоспособного возраста, %": employed_working_age / able_bodied * 100,
    }


def self_test(start: dict, end: dict) -> None:
    for period in (start, end):
        assert period["Рабочая сила"] == period["Занятые, всего"] + period["Безработные, всего"]
        total = period["Занятые / рабочая сила, %"] + period["Уровень безработицы, %"]
        assert abs(total - 100) < 1e-9
    print("Контроль формул пройден: L = E + U, E/L + U/L = 100 %")


def zoom_limits(values, pad_ratio=0.35):
    """Границы оси Y вокруг данных, чтобы различия были видны."""
    lo, hi = min(values), max(values)
    span = hi - lo
    if span <= 0:
        span = max(abs(hi) * 0.02, 1.0)
    pad = span * pad_ratio
    return lo - pad, hi + pad


def style_axis(ax, values):
    """Число знаков на оси подбираем под масштаб, добавляем сетку."""
    span = max(values) - min(values)
    if span < 0.05:
        decimals = 3
    elif span < 0.5:
        decimals = 2
    elif span < 5:
        decimals = 1
    else:
        decimals = 0
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.{decimals}f}"))
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)


def zoomed_pair(ax, title, ylabel, begin, end, unit="", value_fmt="%.2f"):
    """Два столбца (начало/конец) с приближенной шкалой и подписью изменения."""
    values = [begin, end]
    bars = ax.bar(["Начало года", "Конец года"], values,
                  color=[BEGIN_COLOR, END_COLOR], width=0.55)
    ax.bar_label(bars, fmt=value_fmt, fontsize=9)
    ax.set_ylim(zoom_limits(values))
    style_axis(ax, values)
    ax.set_title(f"{title}\nизменение: {end - begin:+.2f}{unit}", fontsize=10)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.tick_params(axis="x", labelsize=9)


def draw_charts(start: dict, end: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Уровень безработицы (обязательная диаграмма)
    fig, ax = plt.subplots(figsize=(7, 4.2))
    zoomed_pair(ax, f"Уровень безработицы: вариант {VARIANT}",
                "Уровень безработицы, %",
                start["Уровень безработицы, %"], end["Уровень безработицы, %"],
                unit=" п. п.")
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.text(0.5, 0.015, ZOOM_NOTE, ha="center", fontsize=8, color="#555555")
    fig.savefig(out_dir / "unemployment_rate.png", dpi=150)
    plt.close(fig)

    # 2. Состав рабочей силы: у каждой панели своя шкала
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 4.4))
    zoomed_pair(axes[0], "Занятые", "Численность, ед. исходной таблицы",
                start["Занятые, всего"], end["Занятые, всего"],
                unit=" ед.", value_fmt="%.0f")
    zoomed_pair(axes[1], "Безработные", "Численность, ед. исходной таблицы",
                start["Безработные, всего"], end["Безработные, всего"],
                unit=" ед.", value_fmt="%.0f")
    fig.suptitle(f"Состав рабочей силы: вариант {VARIANT}", fontsize=12)
    fig.tight_layout(rect=(0, 0.05, 1, 0.94))
    fig.text(0.5, 0.015, ZOOM_NOTE, ha="center", fontsize=8, color="#555555")
    fig.savefig(out_dir / "workforce_structure.png", dpi=150)
    plt.close(fig)

    # 3. Трудовые ресурсы и рабочая сила: у каждой панели своя шкала
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 4.4))
    zoomed_pair(axes[0], "Трудовые ресурсы (учебн.)", "Численность, ед. исходной таблицы",
                start["Трудовые ресурсы (учебн.)"], end["Трудовые ресурсы (учебн.)"],
                unit=" ед.", value_fmt="%.0f")
    zoomed_pair(axes[1], "Рабочая сила", "Численность, ед. исходной таблицы",
                start["Рабочая сила"], end["Рабочая сила"],
                unit=" ед.", value_fmt="%.0f")
    fig.suptitle(f"Трудовые ресурсы и рабочая сила: вариант {VARIANT}", fontsize=12)
    fig.tight_layout(rect=(0, 0.05, 1, 0.94))
    fig.text(0.5, 0.015, ZOOM_NOTE, ha="center", fontsize=8, color="#555555")
    fig.savefig(out_dir / "labour_resources.png", dpi=150)
    plt.close(fig)

    # 4. Относительные показатели: 4 панели со своими шкалами
    panels = [
        ("Занятые / трудовые ресурсы, %", "Занятые / трудовые ресурсы"),
        ("Занятые / рабочая сила, %", "Занятые / рабочая сила"),
        ("Уровень безработицы, %", "Безработные / рабочая сила"),
        ("Трудовые ресурсы / население, %", "Трудовые ресурсы / население"),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(10, 7.5))
    for ax, (key, title) in zip(axes.flat, panels):
        zoomed_pair(ax, title, "Значение, %", start[key], end[key], unit=" п. п.")
    fig.suptitle(f"Система относительных показателей: вариант {VARIANT}", fontsize=13)
    fig.tight_layout(rect=(0, 0.04, 1, 0.95))
    fig.text(0.5, 0.012, ZOOM_NOTE, ha="center", fontsize=8, color="#555555")
    fig.savefig(out_dir / "coefficients.png", dpi=150)
    plt.close(fig)

    # 5. Изменение показателей в п. п. — нулевая база, корректная шкала
    changes = [
        ("Уровень безработицы", "Уровень безработицы, %"),
        ("Зарег. / все безработные", "Зарегистрированные / все безработные, %"),
        ("Занятые / трудовые ресурсы", "Занятые / трудовые ресурсы, %"),
        ("Занятые / рабочая сила", "Занятые / рабочая сила, %"),
        ("Трудовые ресурсы / население", "Трудовые ресурсы / население, %"),
        ("Зарег. / рабочая сила", "Зарегистрированные / рабочая сила, %"),
        ("Рабочая сила / трудовые ресурсы", "Рабочая сила / трудовые ресурсы, %"),
        ("Работающие трудоспособного возраста", "Работающие трудоспособного возраста, %"),
    ]
    rows = sorted(((label, end[key] - start[key]) for label, key in changes),
                  key=lambda item: item[1])
    labels = [row[0] for row in rows]
    deltas = [row[1] for row in rows]
    colors = [END_COLOR if d > 0 else BEGIN_COLOR for d in deltas]

    fig, ax = plt.subplots(figsize=(9.5, 5))
    bars = ax.barh(labels, deltas, color=colors, height=0.6)
    ax.bar_label(bars, fmt="%+.2f", padding=4, fontsize=9)
    ax.axvline(0, color="#333333", linewidth=1)
    ax.set_xlabel("Изменение за период, процентные пункты", fontsize=10)
    ax.set_title(f"Изменение относительных показателей: вариант {VARIANT}", fontsize=12)
    span = max(abs(min(deltas)), abs(max(deltas)))
    ax.set_xlim(-span * 1.35, span * 1.35)
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", labelsize=9)
    handles = [Patch(color=END_COLOR, label="рост показателя"),
               Patch(color=BEGIN_COLOR, label="снижение показателя")]
    ax.legend(handles=handles, loc="lower right", fontsize=9)
    fig.tight_layout()
    fig.savefig(out_dir / "changes.png", dpi=150)
    plt.close(fig)


def print_conclusions(start: dict, end: dict, delta: pd.Series) -> None:
    print("\n" + "=" * 60)
    print(f"ВЫВОДЫ ПО ВАРИАНТУ {VARIANT}")
    print("=" * 60)
    print(
        f"1. Занятые сократились с {start['Занятые, всего']:.0f} до {end['Занятые, всего']:.0f} "
        f"({delta['Занятые, всего']:+.0f}), безработные выросли с {start['Безработные, всего']:.0f} "
        f"до {end['Безработные, всего']:.0f} ({delta['Безработные, всего']:+.0f}). "
        f"Рабочая сила изменилась на {delta['Рабочая сила']:+.0f} ед., то есть её общая численность "
        f"почти не изменилась, а структура сдвинулась в сторону безработицы."
    )
    print(
        f"2. Уровень безработицы вырос с {start['Уровень безработицы, %']:.2f} % "
        f"до {end['Уровень безработицы, %']:.2f} % ({delta['Уровень безработицы, %']:+.2f} п. п.). "
        f"Доля занятых в рабочей силе снизилась на {abs(delta['Занятые / рабочая сила, %']):.2f} п. п."
    )
    print(
        f"3. Зарегистрированных безработных стало больше: {start['Зарегистрированные безработные']:.0f} -> "
        f"{end['Зарегистрированные безработные']:.0f} ({delta['Зарегистрированные безработные']:+.0f}), "
        f"но их доля среди всех безработных снизилась с {start['Зарегистрированные / все безработные, %']:.2f} % "
        f"до {end['Зарегистрированные / все безработные, %']:.2f} % "
        f"({delta['Зарегистрированные / все безработные, %']:+.2f} п. п.). "
        f"Противоречия нет: общая безработица росла быстрее административного учёта, "
        f"это разные совокупности наблюдения."
    )
    print(
        f"4. Трудовые ресурсы по учебной схеме сократились с {start['Трудовые ресурсы (учебн.)']:.0f} "
        f"до {end['Трудовые ресурсы (учебн.)']:.0f} ({delta['Трудовые ресурсы (учебн.)']:+.0f}). "
        f"Их доля в постоянном населении изменилась на {delta['Трудовые ресурсы / население, %']:+.2f} п. п."
    )
    print(
        f"5. Отношение занятых к трудовым ресурсам практически не изменилось "
        f"({delta['Занятые / трудовые ресурсы, %']:+.2f} п. п.): занятые и трудовые ресурсы "
        f"сокращались почти пропорционально."
    )
    print(
        "\nОграничения: расчёт выполнен по упрощённой учебной схеме T = A - I + P + M "
        "без данных о трудовых мигрантах; календарный год и единицы измерения в источнике не указаны; "
        "возрастные границы категорий трактованы условно. Причины изменений по исходной таблице "
        "не устанавливаются, значения нельзя приписывать конкретной территории."
    )
    print(
        "Графики с приближенной шкалой показывают направления изменений наглядно, "
        "но не отражают их существенность: величину изменения следует оценивать "
        "по числовым подписям и по диаграмме изменений в процентных пунктах."
    )


def main() -> None:
    df = load_data(DATA_FILE)
    print(f"Вариант {VARIANT}. Таблица загружена: {df.shape[0]} строк, {df.shape[1]} колонки.")

    for col in (1, 2):
        check_logic(df, col)
    print("Проверка исходных данных и логических ограничений пройдена.")

    start = calc(df, 1)
    end = calc(df, 2)
    self_test(start, end)

    result = pd.DataFrame({"Начало": start, "Конец": end})
    result["Изменение"] = result["Конец"] - result["Начало"]

    print("\nСводная таблица (изменение процентов — в процентных пунктах):")
    print(result.round(2).to_string())

    result.round(2).to_csv(BASE_DIR / "results.csv", encoding="utf-8-sig")
    relative = result.loc[result.index.isin(PERCENT_KEYS)]
    relative.round(2).to_csv(BASE_DIR / "indicators.csv", encoding="utf-8-sig")
    print("\nСохранены results.csv и indicators.csv")

    draw_charts(start, end, CHARTS_DIR)
    print("Сохранены графики в папку charts/ (5 файлов)")

    print_conclusions(start, end, result["Изменение"])


if __name__ == "__main__":
    main()