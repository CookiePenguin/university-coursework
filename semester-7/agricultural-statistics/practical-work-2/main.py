from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# Папка, в которой находится main.py
BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# Исходные данные варианта
df = pd.DataFrame({
    "Культура": [
        "Кормовые корнеплоды",
        "Силосные",
        "Однолетние травы",
        "Многолетние травы",
    ],
    "S0": [1195, 6076, 1676, 22351],
    "S1": [1088, 6574, 2116, 13311],
    "yk": [61.7, 62.4, 25.1, 32.7],
    "yp": [357, 394, 497, 377],
})

# 1. Общие площади
total_s0 = df["S0"].sum()
total_s1 = df["S1"].sum()

# 2. Структура посевных площадей, %
df["d0, %"] = df["S0"] / total_s0 * 100
df["d1, %"] = df["S1"] / total_s1 * 100

# 3. Динамика площадей
df["Изменение площади, га"] = df["S1"] - df["S0"]
df["Индекс площади, %"] = df["S1"] / df["S0"] * 100

# 4. Структурные сдвиги
df["Структурный сдвиг, п.п."] = df["d1, %"] - df["d0, %"]
df["Абсолютный сдвиг, п.п."] = df["Структурный сдвиг, п.п."].abs()

sum_abs_shifts = df["Абсолютный сдвиг, п.п."].sum()
linear_coefficient = sum_abs_shifts / 2

quadratic_coefficient = np.sqrt(
    (df["Структурный сдвиг, п.п."] ** 2).sum() / len(df)
)

ryabtsev_index = np.sqrt(
    (df["Структурный сдвиг, п.п."] ** 2).sum()
    / ((df["d0, %"] + df["d1, %"]) ** 2).sum()
)

# 5. Средняя продуктивность при структуре каждого периода
average_yk_0 = (df["d0, %"] * df["yk"]).sum() / 100
average_yk_1 = (df["d1, %"] * df["yk"]).sum() / 100

average_yp_0 = (df["d0, %"] * df["yp"]).sum() / 100
average_yp_1 = (df["d1, %"] * df["yp"]).sum() / 100

productivity = pd.DataFrame({
    "Показатель": ["Кормовые единицы", "Переваримый протеин"],
    "При структуре S0": [average_yk_0, average_yp_0],
    "При структуре S1": [average_yk_1, average_yp_1],
})

productivity["Изменение"] = (
    productivity["При структуре S1"]
    - productivity["При структуре S0"]
)

productivity["Индекс, %"] = (
    productivity["При структуре S1"]
    / productivity["При структуре S0"]
    * 100
)

# 6. Общие показатели
indicators = pd.DataFrame({
    "Показатель": [
        "Площадь базисного периода, га",
        "Площадь отчётного периода, га",
        "Изменение площади, га",
        "Индекс общей площади, %",
        "Изменение общей площади, %",
        "Сумма абсолютных сдвигов, п.п.",
        "Линейный коэффициент, п.п.",
        "Квадратический коэффициент, п.п.",
        "Индекс Рябцева",
    ],
    "Значение": [
        total_s0,
        total_s1,
        total_s1 - total_s0,
        total_s1 / total_s0 * 100,
        (total_s1 / total_s0 - 1) * 100,
        sum_abs_shifts,
        linear_coefficient,
        quadratic_coefficient,
        ryabtsev_index,
    ],
})

# 7. Проверки правильности структуры
assert np.isclose(df["d0, %"].sum(), 100)
assert np.isclose(df["d1, %"].sum(), 100)
assert np.isclose(df["Структурный сдвиг, п.п."].sum(), 0)

# 8. Сохранение результатов в Excel
excel_path = RESULTS_DIR / "analysis_results.xlsx"

with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="Структура и сдвиги", index=False)
    indicators.to_excel(writer, sheet_name="Общие показатели", index=False)
    productivity.to_excel(writer, sheet_name="Продуктивность", index=False)

# 9. График сравнения площадей
x = np.arange(len(df))
width = 0.35

fig, ax = plt.subplots(figsize=(11, 6))
ax.barh(x - width / 2, df["S0"], width, label="Базисный период")
ax.barh(x + width / 2, df["S1"], width, label="Отчётный период")
ax.set_yticks(x)
ax.set_yticklabels(df["Культура"])
ax.set_xlabel("Площадь, га")
ax.set_title("Сравнение посевных площадей")
ax.legend()
ax.grid(axis="x", alpha=0.3)
fig.tight_layout()
fig.savefig(RESULTS_DIR / "areas_comparison.png", dpi=150)
plt.close(fig)

# 10. График структурных сдвигов
fig, ax = plt.subplots(figsize=(11, 6))

colors = [
    "green" if value >= 0 else "red"
    for value in df["Структурный сдвиг, п.п."]
]

ax.barh(df["Культура"], df["Структурный сдвиг, п.п."], color=colors)
ax.axvline(0, color="black", linewidth=0.8)
ax.set_xlabel("Изменение доли, процентных пунктов")
ax.set_title("Структурные сдвиги в посевных площадях")
ax.grid(axis="x", alpha=0.3)
fig.tight_layout()
fig.savefig(RESULTS_DIR / "structural_shifts.png", dpi=150)
plt.close(fig)

# 11. Вывод результатов
print("=" * 55)
print("ПЗ 2. ОЦЕНКА СТРУКТУРНЫХ СДВИГОВ")
print("=" * 55)

print(f"Площадь базисного периода: {total_s0:.0f} га")
print(f"Площадь отчётного периода: {total_s1:.0f} га")
print(f"Изменение площади: {total_s1 - total_s0:.0f} га")
print(f"Изменение площади: {(total_s1 / total_s0 - 1) * 100:.2f}%")
print(f"Индекс общей площади: {total_s1 / total_s0 * 100:.2f}%")

print("\nСТРУКТУРА И СДВИГИ")
print(
    df[
        ["Культура", "d0, %", "d1, %", "Структурный сдвиг, п.п."]
    ].round(2).to_string(index=False)
)

print("\nПОКАЗАТЕЛИ СТРУКТУРНЫХ СДВИГОВ")
print(f"Сумма абсолютных сдвигов: {sum_abs_shifts:.2f} п.п.")
print(f"Линейный коэффициент: {linear_coefficient:.2f} п.п.")
print(f"Квадратический коэффициент: {quadratic_coefficient:.2f} п.п.")
print(f"Индекс Рябцева: {ryabtsev_index:.4f}")

print("\nСРЕДНЯЯ ПРОДУКТИВНОСТЬ")
print(productivity.round(2).to_string(index=False))

print("\nФайлы сохранены:")
print(f"Excel: {excel_path}")
print(f"График площадей: {RESULTS_DIR / 'areas_comparison.png'}")
print(f"График структурных сдвигов: {RESULTS_DIR / 'structural_shifts.png'}")
print("\nРасчёты завершены.")