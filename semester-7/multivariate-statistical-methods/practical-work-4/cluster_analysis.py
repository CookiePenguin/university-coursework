"""ПЗ №4. Кластерный анализ субъектов ЦФО (евклидово расстояние, 3 метода)."""

import math
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

REGIONS = ["Белгородская", "Воронежская", "Тамбовская", "Московская", "Калужская", "Костромская"]
FEATURES = ["Мясо", "Молоко", "Яйца", "Сахар", "Раст. масло", "Хлеб"]
DATA = [
    [99, 274, 318, 43, 13.6, 135],
    [101, 299, 350, 52, 17.3, 131],
    [84, 162, 206, 55, 17.0, 156],
    [116, 259, 369, 41, 13.1, 120],
    [84, 270, 249, 28, 11.1, 108],
    [68, 228, 354, 29, 9.7, 102],
]

SHEET_DATA = "ИсходныеДанные"
SHEET_DIST = "МатрицаРасстояний"
SHEETS = {"single": ("БлижайшийСосед", "MIN", "Метод ближайшего соседа"),
          "complete": ("ДальнийСосед", "MAX", "Метод дальнего соседа"),
          "upgma": ("UPGMA", "AVERAGE", "Невзвешенное попарное среднее")}

BOLD = Font(bold=True)
TITLE = Font(bold=True, size=14)
MERGE_FILL = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")


def euclid(p, q):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(p, q)))


BASE = [[euclid(DATA[i], DATA[j]) for j in range(len(DATA))] for i in range(len(DATA))]


def link(members_a, members_b, func):
    vals = [BASE[i][j] for i in members_a for j in members_b]
    return func(vals)


LINK_FUNCS = {"single": min, "complete": max, "upgma": lambda v: sum(v) / len(v)}


def clusterize(method):
    """Возвращает список шагов: {clusters, a, b, dist}."""
    func = LINK_FUNCS[method]
    clusters = [[i] for i in range(len(DATA))]
    steps = []
    while len(clusters) > 1:
        best = None
        for a in range(len(clusters)):
            for b in range(a + 1, len(clusters)):
                d = link(clusters[a], clusters[b], func)
                if best is None or d < best[2]:
                    best = (a, b, d)
        a, b, d = best
        steps.append({"clusters": [c[:] for c in clusters], "a": a, "b": b, "dist": d})
        merged = clusters[a] + clusters[b]
        clusters = [c for k, c in enumerate(clusters) if k not in (a, b)]
        clusters.append(merged)
    return steps


def base_cell(i, j):
    return f"{SHEET_DIST}!{get_column_letter(2 + j)}{4 + i}"


def label(members):
    """Красивое название кластера: одиночное имя или 'Имя1 + Имя2'."""
    names = [REGIONS[m] for m in members]
    if len(names) == 1:
        return names[0]
    else:
        return " + ".join(names)


def build(wb):
    # ---------- Лист данных ----------
    ws = wb.active
    ws.title = SHEET_DATA
    ws["A1"] = "ПЗ №4. Потребление продуктов питания на душу населения (2023)"
    ws["A1"].font = TITLE
    ws["A3"] = "Субъект ЦФО"
    for j, f in enumerate(FEATURES):
        ws.cell(row=3, column=2 + j, value=f).font = BOLD
    for i, row in enumerate(DATA):
        ws.cell(row=4 + i, column=1, value=REGIONS[i])
        for j, v in enumerate(row):
            ws.cell(row=4 + i, column=2 + j, value=v)
    ws["A11"] = "Среднее"
    ws["A12"] = "Станд. отклонение"
    ws["A11"].font = BOLD
    ws["A12"].font = BOLD
    for j in range(len(FEATURES)):
        c = get_column_letter(2 + j)
        ws[f"{c}11"] = f"=AVERAGE({c}4:{c}9)"
        ws[f"{c}12"] = f"=STDEV({c}4:{c}9)"
        ws[f"{c}11"].number_format = "0.00"
        ws[f"{c}12"].number_format = "0.00"

    # ---------- Матрица расстояний ----------
    wd = wb.create_sheet(SHEET_DIST)
    wd["A1"] = "Евклидовы расстояния (формулы от исходных данных)"
    wd["A1"].font = TITLE
    for j, r in enumerate(REGIONS):
        wd.cell(row=3, column=2 + j, value=r).font = BOLD
        wd.cell(row=4 + j, column=1, value=r).font = BOLD
    for i in range(len(DATA)):
        for j in range(len(DATA)):
            cell = wd.cell(row=4 + i, column=2 + j)
            if i == j:
                cell.value = 0
            else:
                cell.value = (f"=SQRT(SUMXMY2({SHEET_DATA}!B{4+i}:G{4+i},"
                              f"{SHEET_DATA}!B{4+j}:G{4+j}))")
            cell.number_format = "0.00"

    dendro_rows = {}
    # ---------- Листы методов ----------
    for method, (sheet, func, title) in SHEETS.items():
        wm = wb.create_sheet(sheet)
        wm["A1"] = title
        wm["A1"].font = TITLE
        steps = clusterize(method)
        cursor = 3
        dendro_rows[method] = []
        for s, st in enumerate(steps):
            clusters = st["clusters"]
            m = len(clusters)
            wm.cell(row=cursor, column=1,
                    value=(f"Шаг {s}: начальная матрица расстояний"
                           if s == 0 else
                           f"Шаг {s}: после объединения кластеров")).font = BOLD
            
            # Заголовки таблицы
            hdr = cursor + 1
            for b in range(m):
                wm.cell(row=hdr, column=2 + b, value=label(clusters[b])).font = BOLD
                wm.cell(row=hdr + 1 + b, column=1, value=label(clusters[b])).font = BOLD
            
            # Заполнение матрицы
            for a in range(m):
                for b in range(m):
                    cell = wm.cell(row=hdr + 1 + a, column=2 + b)
                    if a == b:
                        cell.value = 0
                    else:
                        refs = [base_cell(i, j) for i in clusters[a] for j in clusters[b]]
                        cell.value = "=" + func + "(" + ",".join(refs) + ")"
                    cell.number_format = "0.00"
            
            # Подсветка ячейки слияния
            wm.cell(row=hdr + 1 + st["a"], column=2 + st["b"]).fill = MERGE_FILL
            
            # Сохраняем ссылку на расстояние для дендрограммы
            dendro_rows[method].append(
                (st["clusters"][st["a"]], st["clusters"][st["b"]],
                 f"{sheet}!{get_column_letter(2 + st['b'])}{hdr + 1 + st['a']}"))
            cursor = hdr + 1 + m + 2

    # ---------- Дендрограмма ----------
    wdend = wb.create_sheet("Дендрограмма")
    wdend["A1"] = "Схема объединения объектов и кластеров"
    wdend["A1"].font = TITLE
    row = 3
    for method, (sheet, func, title) in SHEETS.items():
        wdend.cell(row=row, column=1, value=title).font = BOLD
        row += 1
        for k, (ca, cb, ref) in enumerate(dendro_rows[method], start=1):
            wdend.cell(row=row, column=1,
                       value=f"Шаг {k}: объединить [{label(ca)}] и [{label(cb)}], расстояние =")
            wdend.cell(row=row, column=5, value=f"={ref}").number_format = "0.00"
            row += 1
        row += 1

    # ---------- Характеристика кластеров ----------
    wc = wb.create_sheet("Кластеры")
    wc["A1"] = "Характеристика кластеров (средние по исходным данным, формулы)"
    wc["A1"].font = TITLE
    
    cuts = [
        ("Основной разрез: 2 кластера", [
            ("Кластер 1: регионы с повышенным потреблением", [0, 1, 3, 4, 5]),
            ("Кластер 2: низкоживотный профиль (Тамбовская)", [2]),
        ]),
        ("Дополнительный разрез: 3 кластера", [
            ("Кластер A: ядро с высоким потреблением", [0, 1, 3, 5]),
            ("Кластер B: низкое потребление сахара и хлеба (Калужская)", [4]),
            ("Кластер C: низкоживотный профиль (Тамбовская)", [2]),
        ]),
    ]
    row = 3
    for cut_title, groups in cuts:
        wc.cell(row=row, column=1, value=cut_title).font = BOLD
        row += 1
        wc.cell(row=row, column=1, value="Признак").font = BOLD
        for g, (name, _) in enumerate(groups):
            wc.cell(row=row, column=2 + g, value=name).font = BOLD
        row += 1
        for j, f in enumerate(FEATURES):
            wc.cell(row=row, column=1, value=f)
            for g, (_, members) in enumerate(groups):
                refs = [f"{SHEET_DATA}!{get_column_letter(2+j)}{4+m}" for m in members]
                cell = wc.cell(row=row, column=2 + g, value="=AVERAGE(" + ",".join(refs) + ")")
                cell.number_format = "0.00"
            row += 1
        row += 2
    wc.cell(row=row, column=1,
            value="Обоснование: наибольший скачок расстояния объединения наблюдается на последнем шаге "
                  "всех трёх методов, поэтому базовым выбран разрез на 2 кластера.").font = Font(italic=True)


def main():
    wb = Workbook()
    build(wb)
    wb.save("cluster_analysis.xlsx")
    print("✅ Excel создан: cluster_analysis.xlsx")
    print("🎉 Теперь названия кластеров выглядят красиво и академично!")


if __name__ == "__main__":
    main()