"""ПР №6. Дискриминантный анализ: Excel с формулами + контрольный расчёт на Python."""

from pathlib import Path

from openpyxl import Workbook


# ============================================================
# Контрольный расчёт на чистом Python (для сверки с Excel)
# ============================================================
def mat_mul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))]
            for i in range(len(A))]


def transpose(M):
    return [[M[j][i] for j in range(len(M))] for i in range(len(M[0]))]


def means(M):
    return [sum(r[j] for r in M) / len(M) for j in range(len(M[0]))]


def deviations(M, mu):
    return [[M[i][j] - mu[j] for j in range(len(mu))] for i in range(len(M))]


def scatter(dev):
    return mat_mul(transpose(dev), dev)


def det3(M):
    return (M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1])
            - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0])
            + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0]))


def inv3(M):
    d = det3(M)
    c = [
        [+(M[1][1] * M[2][2] - M[1][2] * M[2][1]), -(M[0][1] * M[2][2] - M[0][2] * M[2][1]), +(M[0][1] * M[1][2] - M[0][2] * M[1][1])],
        [-(M[1][0] * M[2][2] - M[1][2] * M[2][0]), +(M[0][0] * M[2][2] - M[0][2] * M[2][0]), -(M[0][0] * M[1][2] - M[0][2] * M[1][0])],
        [+(M[1][0] * M[2][1] - M[1][1] * M[2][0]), -(M[0][0] * M[2][1] - M[0][1] * M[2][0]), +(M[0][0] * M[1][1] - M[0][1] * M[1][0])],
    ]
    return [[c[j][i] / d for j in range(3)] for i in range(3)]


def mat_vec(M, v):
    return [sum(M[i][j] * v[j] for j in range(len(v))) for i in range(len(M))]


def quad(a, M):
    return sum(a[i] * M[i][j] * a[j] for i in range(len(a)) for j in range(len(a)))


NORM = [[8.5, 9.8, 4.3], [9.1, 10.1, 4.6], [8.6, 9.9, 4.4], [8.9, 10.2, 4.8], [8.8, 10.0, 4.5]]
PATH = [[5.6, 8.7, 3.4], [5.9, 8.8, 3.3], [5.7, 8.4, 3.5], [6.0, 8.6, 3.4], [5.8, 8.5, 3.7]]
X_ENT = [[224.228, 17.115, 22.981], [151.827, 14.904, 21.481],
         [147.313, 13.627, 28.669], [152.253, 10.545, 10.199]]
Y_ENT = [[46.757, 4.428, 11.124], [29.033, 5.510, 6.091],
         [52.134, 4.214, 11.842], [37.050, 5.527, 11.873], [63.979, 4.211, 12.860]]
Z_ENT = [55.41, 9.592, 12.84]


def solve_task1():
    n_mu, p_mu = means(NORM), means(PATH)
    N = scatter(deviations(NORM, n_mu))
    P = scatter(deviations(PATH, p_mu))
    S = [[(N[i][j] + P[i][j]) / 8 for j in range(3)] for i in range(3)]
    diff = [n_mu[j] - p_mu[j] for j in range(3)]
    a = mat_vec(inv3(S), diff)
    Xn = sum(a[j] * n_mu[j] for j in range(3))
    Xp = sum(a[j] * p_mu[j] for j in range(3))
    Sn2 = quad(a, N) / 4
    Sp2 = quad(a, P) / 4
    Sn, Sp = Sn2 ** 0.5, Sp2 ** 0.5
    X0 = (Xn * Sp + Xp * Sn) / (Sn + Sp)
    return a, Xn, Xp, Sn, Sp, X0


def solve_task2():
    x_mu, y_mu = means(X_ENT), means(Y_ENT)
    Sx = [[scatter(deviations(X_ENT, x_mu))[i][j] / 3 for j in range(3)] for i in range(3)]
    Sy = [[scatter(deviations(Y_ENT, y_mu))[i][j] / 4 for j in range(3)] for i in range(3)]
    Sp = [[(3 * Sx[i][j] + 4 * Sy[i][j]) / 7 for j in range(3)] for i in range(3)]
    diff = [x_mu[j] - y_mu[j] for j in range(3)]
    a = mat_vec(inv3(Sp), diff)
    fx = [sum(a[j] * r[j] for j in range(3)) for r in X_ENT]
    fy = [sum(a[j] * r[j] for j in range(3)) for r in Y_ENT]
    C = (sum(fx) / len(fx) + sum(fy) / len(fy)) / 2
    fz = sum(a[j] * Z_ENT[j] for j in range(3))
    return a, fx, fy, C, fz


# ============================================================
# Генерация Excel (все вычисляемые ячейки — формулы)
# ============================================================
def build_workbook(out_path: Path) -> None:
    wb = Workbook()

    # ---------------- Лист 1: Задача 1 ----------------
    ws = wb.active
    ws.title = "Задача1"
    ws["A1"] = "ЗАДАЧА 1. Дискриминантный анализ (коровы)"

    ws["B2"], ws["C2"], ws["D2"] = "X1", "X2", "X3"
    ws["G2"], ws["H2"], ws["I2"] = "X1", "X2", "X3"
    for i, row in enumerate(NORM, start=3):
        for j, val in enumerate(row, start=2):
            ws.cell(row=i, column=j, value=val)
    for i, row in enumerate(PATH, start=3):
        for j, val in enumerate(row, start=7):
            ws.cell(row=i, column=j, value=val)

    # Средние (строка 9)
    ws["A9"] = "Средние значения:"
    for col in ("B", "C", "D", "G", "H", "I"):
        ws[f"{col}9"] = f"=AVERAGE({col}3:{col}7)"

    # Матрицы отклонений Mn (B12:D16), Mp (G12:I16)
    ws["A11"] = "Матрица отклонений Mn (норма):"
    ws["F11"] = "Матрица отклонений Mp (патология):"
    for i in range(12, 17):
        src = i - 9
        for col in ("B", "C", "D"):
            ws[f"{col}{i}"] = f"={col}{src}-{col}$9"
        for col in ("G", "H", "I"):
            ws[f"{col}{i}"] = f"={col}{src}-{col}$9"

    # Транспонированные матрицы MnT (B19:F21), MpT (G19:K21)
    ws["A18"] = "Транспонированная MnT:"
    ws["F18"] = "Транспонированная MpT:"
    for r in range(3):
        for c in range(5):
            ws.cell(row=19 + r, column=2 + c, value=f"={chr(ord('B') + r)}{12 + c}")
            ws.cell(row=19 + r, column=7 + c, value=f"={chr(ord('G') + r)}{12 + c}")

    # Дискриминантные матрицы N (B24:D26), P (G24:I26) = MnT * Mn
    ws["A23"] = "Дискриминантная матрица N = MnT*Mn:"
    ws["F23"] = "Дискриминантная матрица P = MpT*Mp:"
    for r in range(3):
        for c in range(3):
            ws.cell(row=24 + r, column=2 + c,
                    value=f"=SUMPRODUCT($B{19 + r}:$F{19 + r},$B{19 + c}:$F{19 + c})")
            ws.cell(row=24 + r, column=7 + c,
                    value=f"=SUMPRODUCT($G{19 + r}:$K{19 + r},$G{19 + c}:$K{19 + c})")

    # Ковариационная матрица S = (N+P)/8 (B29:D31)
    ws["A28"] = "Ковариационная матрица S = (N+P)/8:"
    partner = {"B": "G", "C": "H", "D": "I"}
    for r in range(3):
        for col in ("B", "C", "D"):
            ws[f"{col}{29 + r}"] = f"=({col}{24 + r}+{partner[col]}{24 + r})/8"

    # Вектор разности n-p (G29:G31)
    ws["F28"] = "Вектор разности (n-p):"
    ws["G29"] = "=B9-G9"
    ws["G30"] = "=C9-H9"
    ws["G31"] = "=D9-I9"

    # Определитель S (C33)
    ws["A33"] = "Определитель S:"
    ws["C33"] = ("=B29*(C30*D31-D30*C31)-C29*(B30*D31-D30*B31)+D29*(B30*C31-C30*B31)")

    # Обратная матрица S^-1 (B36:D38)
    ws["A35"] = "Обратная матрица S^-1:"
    ws["B36"] = "=(C30*D31-D30*C31)/$C$33"
    ws["C36"] = "=(D29*C31-C29*D31)/$C$33"
    ws["D36"] = "=(C29*D30-D29*C30)/$C$33"
    ws["B37"] = "=(D30*B31-B30*D31)/$C$33"
    ws["C37"] = "=(B29*D31-D29*B31)/$C$33"
    ws["D37"] = "=(D29*B30-B29*D30)/$C$33"
    ws["B38"] = "=(B30*C31-C30*B31)/$C$33"
    ws["C38"] = "=(C29*B31-B29*C31)/$C$33"
    ws["D38"] = "=(B29*C30-C29*B30)/$C$33"

    # Коэффициенты a (G36:G38)
    ws["F35"] = "Коэффициенты уравнения:"
    ws["F36"], ws["F37"], ws["F38"] = "a1 =", "a2 =", "a3 ="
    ws["G36"] = "=B36*$G$29+C36*$G$30+D36*$G$31"
    ws["G37"] = "=B37*$G$29+C37*$G$30+D37*$G$31"
    ws["G38"] = "=B38*$G$29+C38*$G$30+D38*$G$31"

    # Xn, Xp
    ws["A40"], ws["B40"] = "Xn =", "=G36*B9+G37*C9+G38*D9"
    ws["A41"], ws["B41"] = "Xp =", "=G36*G9+G37*H9+G38*I9"

    # Дисперсии (квадратичные формы) и стандартные отклонения
    ws["A43"], ws["B43"] = "Sn^2 =", ("=(G36*G36*B24+G36*G37*C24+G36*G38*D24+G37*G36*C24+G37*G37*C25"
                                       "+G37*G38*D25+G38*G36*D24+G38*G37*D25+G38*G38*D26)/4")
    ws["A44"], ws["B44"] = "Sp^2 =", ("=(G36*G36*G24+G36*G37*H24+G36*G38*I24+G37*G36*H24+G37*G37*H25"
                                       "+G37*G38*I25+G38*G36*I24+G38*G37*I25+G38*G38*I26)/4")
    ws["A46"], ws["B46"] = "Sn =", "=SQRT(B43)"
    ws["A47"], ws["B47"] = "Sp =", "=SQRT(B44)"

    # Граница раздела X0
    ws["A49"], ws["B49"] = "X0 =", "=(B40*B47+B41*B46)/(B46+B47)"
    ws["A51"] = "Уравнение: X = a1*X1 + a2*X2 + a3*X3; правило: X - X0 > 0 -> норма"

    # Проверка (подписи БЕЗ знака "=")
    ws["A53"] = "Проверка, норма (X - X0, должно быть > 0):"
    ws["E53"] = "Проверка, патология (X - X0, должно быть < 0):"
    for k in range(5):
        row = 54 + k
        src = 3 + k
        ws[f"B{row}"] = f"Корова {k + 1}:"
        ws[f"C{row}"] = f"=$G$36*B{src}+$G$37*C{src}+$G$38*D{src}-$B$49"
        ws[f"F{row}"] = f"Корова {k + 1}:"
        ws[f"G{row}"] = f"=$G$36*G{src}+$G$37*H{src}+$G$38*I{src}-$B$49"

    # Первичная статистика (этап 1)
    ws["A61"] = "Первичная статистика (проверка близости к нормали):"
    for j, h in enumerate(["Группа", "Признак", "Среднее", "Мода", "Медиана", "Асимметрия", "Эксцесс"]):
        ws.cell(row=62, column=1 + j, value=h)
    stat_rows = [
        ("Норма", "X1", "B3:B7"), ("Норма", "X2", "C3:C7"), ("Норма", "X3", "D3:D7"),
        ("Патология", "X1", "G3:G7"), ("Патология", "X2", "H3:H7"), ("Патология", "X3", "I3:I7"),
    ]
    for k, (grp, feat, rng) in enumerate(stat_rows):
        r = 63 + k
        ws[f"A{r}"] = grp
        ws[f"B{r}"] = feat
        ws[f"C{r}"] = f"=AVERAGE({rng})"
        ws[f"D{r}"] = f'=IFERROR(MODE({rng}),"нет")'
        ws[f"E{r}"] = f"=MEDIAN({rng})"
        ws[f"F{r}"] = f"=SKEW({rng})"
        ws[f"G{r}"] = f"=KURT({rng})"

    # ---------------- Лист 2: Задача 2 ----------------
    ws2 = wb.create_sheet("Задача2")
    ws2["A1"] = "ЗАДАЧА 2. Дискриминантный анализ (предприятия)"
    ws2["B2"], ws2["C2"], ws2["D2"] = "ОПФ", "ППП", "Прибыль"
    ws2["F2"], ws2["G2"], ws2["H2"] = "ОПФ", "ППП", "Прибыль"
    for i, row in enumerate(X_ENT, start=3):
        for j, val in enumerate(row, start=2):
            ws2.cell(row=i, column=j, value=val)
    for i, row in enumerate(Y_ENT, start=3):
        for j, val in enumerate(row, start=6):
            ws2.cell(row=i, column=j, value=val)
    ws2["L1"] = "Новое предприятие Z:"
    ws2["L2"], ws2["M2"], ws2["N2"] = "ОПФ", "ППП", "Прибыль"
    ws2["L3"], ws2["M3"], ws2["N3"] = Z_ENT

    # Средние (строка 9)
    ws2["A9"] = "Средние значения:"
    for col in ("B", "C", "D", "F", "G", "H"):
        ws2[f"{col}9"] = f"=AVERAGE({col}3:{col}{'6' if col in 'BCD' else '7'})"

    # Отклонения Mx (B12:D15), My (F12:H16)
    ws2["A11"] = "Матрица отклонений Mx:"
    ws2["E11"] = "Матрица отклонений My:"
    for i in range(12, 16):
        for col in ("B", "C", "D"):
            ws2[f"{col}{i}"] = f"={col}{i - 8}-{col}$9"
    for i in range(12, 17):
        for col in ("F", "G", "H"):
            ws2[f"{col}{i}"] = f"={col}{i - 8}-{col}$9"

    # Транспонированные MxT (B19:E21), MyT (F19:J21)
    ws2["A18"] = "Транспонированная MxT:"
    ws2["E18"] = "Транспонированная MyT:"
    for r in range(3):
        for c in range(4):
            ws2.cell(row=19 + r, column=2 + c, value=f"={chr(ord('B') + r)}{12 + c}")
        for c in range(5):
            ws2.cell(row=19 + r, column=6 + c, value=f"={chr(ord('F') + r)}{12 + c}")

    # Sx (B24:D26) /3, Sy (F24:H26) /4
    ws2["A23"] = "Ковариационная матрица Sx:"
    ws2["E23"] = "Ковариационная матрица Sy:"
    for r in range(3):
        for c in range(3):
            ws2.cell(row=24 + r, column=2 + c,
                     value=f"=SUMPRODUCT($B{19 + r}:$E{19 + r},$B{19 + c}:$E{19 + c})/3")
            ws2.cell(row=24 + r, column=6 + c,
                     value=f"=SUMPRODUCT($F{19 + r}:$J{19 + r},$F{19 + c}:$J{19 + c})/4")

    # S_pool (B29:D31) = (3*Sx + 4*Sy)/7
    ws2["A28"] = "Объединённая матрица S_pool = (3*Sx+4*Sy)/7:"
    partner2 = {"B": "F", "C": "G", "D": "H"}
    for r in range(3):
        for col in ("B", "C", "D"):
            ws2[f"{col}{29 + r}"] = f"=(3*{col}{24 + r}+4*{partner2[col]}{24 + r})/7"

    # Вектор разности (G29:G31)
    ws2["F28"] = "Вектор разности:"
    ws2["G29"] = "=B9-F9"
    ws2["G30"] = "=C9-G9"
    ws2["G31"] = "=D9-H9"

    # Определитель (C33)
    ws2["A33"] = "Определитель S_pool:"
    ws2["C33"] = ("=B29*(C30*D31-D30*C31)-C29*(B30*D31-D30*B31)+D29*(B30*C31-C30*B31)")

    # Обратная матрица (B36:D38)
    ws2["A35"] = "Обратная матрица S_pool^-1:"
    ws2["B36"] = "=(C30*D31-D30*C31)/$C$33"
    ws2["C36"] = "=(D29*C31-C29*D31)/$C$33"
    ws2["D36"] = "=(C29*D30-D29*C30)/$C$33"
    ws2["B37"] = "=(D30*B31-B30*D31)/$C$33"
    ws2["C37"] = "=(B29*D31-D29*B31)/$C$33"
    ws2["D37"] = "=(D29*B30-B29*D30)/$C$33"
    ws2["B38"] = "=(B30*C31-C30*B31)/$C$33"
    ws2["C38"] = "=(C29*B31-B29*C31)/$C$33"
    ws2["D38"] = "=(B29*C30-C29*B30)/$C$33"

    # Коэффициенты a (G36:G38)
    ws2["F35"] = "Коэффициенты дискриминации:"
    ws2["F36"], ws2["F37"], ws2["F38"] = "a1 =", "a2 =", "a3 ="
    ws2["G36"] = "=B36*$G$29+C36*$G$30+D36*$G$31"
    ws2["G37"] = "=B37*$G$29+C37*$G$30+D37*$G$31"
    ws2["G38"] = "=B38*$G$29+C38*$G$30+D38*$G$31"

    # Значения F для X (C41:C44) и Y (G41:G45)
    ws2["A40"] = "Значения F для передовых:"
    ws2["E40"] = "Значения F для остальных:"
    for k in range(4):
        r = 41 + k
        src = 3 + k
        ws2[f"B{r}"] = f"X{k + 1}:"
        ws2[f"C{r}"] = f"=$G$36*B{src}+$G$37*C{src}+$G$38*D{src}"
    for k in range(5):
        r = 41 + k
        src = 3 + k
        ws2[f"F{r}"] = f"Y{k + 1}:"
        ws2[f"G{r}"] = f"=$G$36*F{src}+$G$37*G{src}+$G$38*H{src}"

    # Средние F и константа C
    ws2["A47"], ws2["B47"] = "F среднее (X) =", "=AVERAGE(C41:C44)"
    ws2["A48"], ws2["B48"] = "F среднее (Y) =", "=AVERAGE(G41:G45)"
    ws2["A49"], ws2["B49"] = "Константа C =", "=(B47+B48)/2"

    # F(Z) и вывод
    ws2["A51"], ws2["B51"] = "F(Z) =", "=$G$36*L3+$G$37*M3+$G$38*N3"
    ws2["A53"] = "Вывод:"
    ws2["B53"] = '=IF(B51>B49,"Z относится к ПЕРЕДОВЫМ (X)","Z относится к ОСТАЛЬНЫМ (Y)")'

    out_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out_path)


def main() -> None:
    base = Path(__file__).resolve().parent
    out = base / "discriminant_analysis.xlsx"
    build_workbook(out)
    print(f"Excel создан: {out}")

    a1, Xn, Xp, Sn, Sp, X0 = solve_task1()
    print("\n=== ЗАДАЧА 1 (контроль для сверки с Excel) ===")
    print(f"a1={a1[0]:.4f}  a2={a1[1]:.4f}  a3={a1[2]:.4f}")
    print(f"Xn={Xn:.4f}  Xp={Xp:.4f}  Sn={Sn:.4f}  Sp={Sp:.4f}  X0={X0:.4f}")
    print("Проверка норма (>0):",
          [round(sum(a1[j] * r[j] for j in range(3)) - X0, 2) for r in NORM])
    print("Проверка патология (<0):",
          [round(sum(a1[j] * r[j] for j in range(3)) - X0, 2) for r in PATH])

    a2, fx, fy, C, fz = solve_task2()
    print("\n=== ЗАДАЧА 2 (контроль для сверки с Excel) ===")
    print(f"a1={a2[0]:.4f}  a2={a2[1]:.4f}  a3={a2[2]:.4f}")
    print(f"F(X) = {[round(v, 2) for v in fx]}")
    print(f"F(Y) = {[round(v, 2) for v in fy]}")
    print(f"C={C:.4f}  F(Z)={fz:.4f}  -> {'ПЕРЕДОВЫЕ' if fz > C else 'ОСТАЛЬНЫЕ'}")


if __name__ == "__main__":
    main()