"""ПЗ №5. Кластерный анализ с/х предприятий (Вариант 12). Формулы в ячейках Excel."""

import numpy as np
from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter
from scipy.cluster.hierarchy import linkage, fcluster
from sklearn.cluster import KMeans

# Выручка, Угодья(га), Работники, Себестоимость, Затраты(тыс.руб), Энергоресурсы(л.с), Балл
DATA = [
    [16500, 3785, 60, 20387, 30152, 15443, 60],
    [48229, 6232, 147, 56718, 75432, 29228, 76],
    [73296, 5182.24, 209, 74979, 90812, 35706, 121],
    [106643, 5338, 262, 90538, 118489, 42704, 134],
    [109327, 3462, 221, 95489, 76598, 31712, 144],
    [6174, 2608, 38, 5796, 9426, 10093, 54],
    [7324, 2107, 27, 7831, 10655, 8281, 57],
    [51411, 3552, 169, 47664, 67371, 24544, 123],
    [7809, 2864, 56, 11926, 16989, 11141, 55],
    [23380, 2551, 57, 21479, 32973, 12908, 84],
    [8451, 1331, 87, 10848, 15863, 5670, 65],
    [25889, 2874, 69, 26382, 39249, 14427, 82],
    [97804, 667, 247, 90674, 147206, 6670, 157],
    [37682, 3441, 166, 39293, 63585, 18237, 94],
    [21535, 3043, 78, 21842, 39994, 13998, 72],
    [15333, 3941, 88, 22631, 34512, 16040, 59],
    [26598, 915, 79, 24406, 38250, 8363, 142],
    [20267, 2271, 69, 23130, 41737, 11355, 81],
    [47119, 3530, 194, 43730, 84388, 21674, 115],
    [46943, 2418, 126, 45028, 47954, 18667, 131],
    [26886, 925, 103, 29206, 48657, 8436, 142],
    [29342, 3787, 120, 28800, 42001, 17799, 78],
    [79880, 3595, 224, 68793, 100563, 29084, 137],
    [44579, 3197, 199, 42337, 69896, 21452, 119],
    [13823, 1861, 60, 20032, 32936, 8002, 75],
    [10302, 2279, 42, 11768, 18553, 9321, 60],
    [51562, 3172, 162, 44456, 65214, 22870, 126],
    [58921, 4237, 69, 62707, 36714, 28388, 118],
    [60170, 3151, 192, 92265, 65845, 23916, 130],
    [19865, 4936, 103, 21067, 28782, 19941, 57],
]

RAW = np.array(DATA, dtype=float)
N = len(RAW)

# Показатели интенсивности (по заданию ПЗ №5)
X = np.column_stack([
    RAW[:, 2] / RAW[:, 1] * 100,   # x1 работники на 100 га
    RAW[:, 5] / RAW[:, 1] * 100,   # x2 энергоресурсы на 100 га
    RAW[:, 4] / RAW[:, 1],         # x3 затраты на 1 га
    RAW[:, 6],                     # x4 балл почвы
])

MU = X.mean(axis=0)
SD = X.std(axis=0, ddof=1)
Z = (X - MU) / SD

HIER = fcluster(linkage(Z, method="ward"), t=3, criterion="maxclust")
KM = KMeans(n_clusters=3, random_state=42, n_init=10).fit_predict(Z) + 1

S_DATA = "ИсходныеДанные"
S_Z = "Стандартизация"
S_DIST = "МатрицаРасстояний"
S_CL = "Кластеризация"
S_PROF = "Характеристика"

BOLD = Font(bold=True)


def build(path="cluster_analysis_var12.xlsx"):
    wb = Workbook()

    # ---------- Лист 1: данные + показатели ----------
    ws = wb.active
    ws.title = S_DATA
    headers = ["N", "Выручка", "Угодья (га)", "Работники (чел)", "Себестоимость",
               "Затраты (тыс.руб)", "Энергоресурсы (л.с)", "Балл почв",
               "x1 (раб/100га)", "x2 (эн/100га)", "x3 (затр/га)", "x4 (балл)"]
    for c, h in enumerate(headers, 1):
        ws.cell(row=1, column=c, value=h).font = BOLD

    for i, row in enumerate(RAW):
        r = i + 2
        ws.cell(row=r, column=1, value=i + 1)          # N — обязательно!
        for j, v in enumerate(row):
            ws.cell(row=r, column=j + 2, value=float(v))
        ws.cell(row=r, column=9, value=f"=D{r}/C{r}*100")
        ws.cell(row=r, column=10, value=f"=G{r}/C{r}*100")
        ws.cell(row=r, column=11, value=f"=F{r}/C{r}")
        ws.cell(row=r, column=12, value=f"=H{r}")
        for c in range(9, 13):
            ws.cell(row=r, column=c).number_format = "0.00"

    ws["A33"] = "Среднее"
    ws["A34"] = "Ст. отклонение"
    ws["A33"].font = BOLD
    ws["A34"].font = BOLD
    for c in range(9, 13):
        L = get_column_letter(c)
        ws[f"{L}33"] = f"=AVERAGE({L}2:{L}31)"
        ws[f"{L}34"] = f"=STDEV({L}2:{L}31)"
        ws[f"{L}33"].number_format = "0.00"
        ws[f"{L}34"].number_format = "0.00"
    for c in range(1, 13):
        ws.column_dimensions[get_column_letter(c)].width = 16

    # ---------- Лист 2: Z-оценки ----------
    wz = wb.create_sheet(S_Z)
    wz["A1"] = "N"
    for c, h in enumerate(["Z x1", "Z x2", "Z x3", "Z x4"], 2):
        wz.cell(row=1, column=c, value=h).font = BOLD
    for i in range(N):
        r = i + 2
        wz.cell(row=r, column=1, value=i + 1)
        for j, src in enumerate(["I", "J", "K", "L"]):
            wz.cell(row=r, column=j + 2,
                    value=(f"=({S_DATA}!{src}{r}-AVERAGE({S_DATA}!{src}$2:{src}$31))"
                           f"/STDEV({S_DATA}!{src}$2:{src}$31)")).number_format = "0.0000"
    for c in range(1, 6):
        wz.column_dimensions[get_column_letter(c)].width = 14

    # ---------- Лист 3: матрица евклидовых расстояний ----------
    wd = wb.create_sheet(S_DIST)
    wd["A1"] = "N"
    for i in range(N):
        wd.cell(row=1, column=i + 2, value=i + 1).font = BOLD
        wd.cell(row=i + 2, column=1, value=i + 1).font = BOLD
    for i in range(N):
        for j in range(N):
            cell = wd.cell(row=i + 2, column=j + 2)
            if i == j:
                cell.value = 0
            else:
                cell.value = (f"=SQRT(SUMXMY2({S_Z}!$B{i+2}:$E{i+2},"
                              f"{S_Z}!$B{j+2}:$E{j+2}))")
            cell.number_format = "0.00"
    for c in range(1, N + 2):
        wd.column_dimensions[get_column_letter(c)].width = 7

    # ---------- Лист 4: результаты кластеризации ----------
    wc = wb.create_sheet(S_CL)
    for c, h in enumerate(["N", "Иерархический (Уорд, k=3)", "K-средних (k=3)"], 1):
        wc.cell(row=1, column=c, value=h).font = BOLD
    for i in range(N):
        wc.cell(row=i + 2, column=1, value=i + 1)
        wc.cell(row=i + 2, column=2, value=int(HIER[i]))
        wc.cell(row=i + 2, column=3, value=int(KM[i]))
    wc["A33"] = "Размер кластера 1"
    wc["A34"] = "Размер кластера 2"
    wc["A35"] = "Размер кластера 3"
    for k in range(1, 4):
        wc.cell(row=32 + k, column=2, value=f"=COUNTIF(B$2:B$31,{k})")
        wc.cell(row=32 + k, column=3, value=f"=COUNTIF(C$2:C$31,{k})")
    for c in range(1, 4):
        wc.column_dimensions[get_column_letter(c)].width = 26

    # ---------- Лист 5: характеристика кластеров ----------
    wp = wb.create_sheet(S_PROF)
    names = ["x1 (раб/100га)", "x2 (эн/100га)", "x3 (затр/га)", "x4 (балл)"]
    row = 1
    for title, col in [("K-средних (k=3)", "C"), ("Иерархический Уорд (k=3)", "B")]:
        wp.cell(row=row, column=1, value=title).font = BOLD
        row += 1
        wp.cell(row=row, column=1, value="Показатель").font = BOLD
        for k in range(1, 4):
            wp.cell(row=row, column=k + 1, value=f"Кластер {k}").font = BOLD
        row += 1
        for j, (name, src) in enumerate(zip(names, ["I", "J", "K", "L"])):
            wp.cell(row=row + j, column=1, value=name)
            for k in range(1, 4):
                wp.cell(row=row + j, column=k + 1,
                        value=(f"=AVERAGEIF({S_CL}!${col}$2:${col}$31,{k},"
                               f"{S_DATA}!{src}$2:{src}$31)")).number_format = "0.00"
        row += len(names) + 2
    wp.cell(row=row, column=1,
            value="Кластеризация выполнена по стандартизированным показателям интенсивности x1-x4.")
    for c in range(1, 5):
        wp.column_dimensions[get_column_letter(c)].width = 24

    wb.save(path)
    return path


def main():
    path = build()
    print(f"Excel создан: {path}\n")
    print("=== КОНТРОЛЬ: показатели интенсивности (первые 5 предприятий) ===")
    for i in range(5):
        print(f"  N{i+1}: x1={X[i,0]:.2f}  x2={X[i,1]:.2f}  x3={X[i,2]:.2f}  x4={X[i,3]:.2f}")
    print("\nСредние x1..x4:", [round(v, 2) for v in MU])
    print("Ст. отклонения x1..x4:", [round(v, 2) for v in SD])
    print("\nРазмеры кластеров (Уорд):", [int((HIER == k).sum()) for k in (1, 2, 3)])
    print("Размеры кластеров (K-средних):", [int((KM == k).sum()) for k in (1, 2, 3)])
    for label, lab in [("K-средних", KM), ("Уорд", HIER)]:
        print(f"\nСредние по кластерам — {label}:")
        for k in (1, 2, 3):
            print(f"  кластер {k}:", [round(v, 2) for v in X[lab == k].mean(axis=0)])
    print("\nПроверка расстояния N1-N2 (евклид по Z):",
          round(float(np.sqrt(((Z[0] - Z[1]) ** 2).sum())), 2))


if __name__ == "__main__":
    main()