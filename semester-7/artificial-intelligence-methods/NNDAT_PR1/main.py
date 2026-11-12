import time

import numpy as np

# ==========================================
# ЗАДАЧА 1: Функции для матричных операций
# ==========================================

def matrix_add(A, B):
    """Сложение двух матриц."""
    if len(A) != len(B) or len(A[0]) != len(B[0]):
        raise ValueError("Матрицы должны быть одного размера")
    rows, cols = len(A), len(A[0])
    C = [[0] * cols for _ in range(rows)]
    for i in range(rows):
        for j in range(cols):
            C[i][j] = A[i][j] + B[i][j]
    return C

def matrix_scalar_mul(A, scalar):
    """Умножение матрицы на число."""
    rows, cols = len(A), len(A[0])
    C = [[0] * cols for _ in range(rows)]
    for i in range(rows):
        for j in range(cols):
            C[i][j] = A[i][j] * scalar
    return C

def matrix_elementwise_mul(A, B):
    """Поэлементное умножение матриц."""
    if len(A) != len(B) or len(A[0]) != len(B[0]):
        raise ValueError("Матрицы должны быть одного размера")
    rows, cols = len(A), len(A[0])
    C = [[0] * cols for _ in range(rows)]
    for i in range(rows):
        for j in range(cols):
            C[i][j] = A[i][j] * B[i][j]
    return C

def matrix_dot(A, B):
    """Скалярное произведение матриц."""
    rows_A, cols_A = len(A), len(A[0])
    rows_B, cols_B = len(B), len(B[0])
    if cols_A != rows_B:
        raise ValueError("Число столбцов A должно равняться числу строк B")
    C = [[0] * cols_B for _ in range(rows_A)]
    for i in range(rows_A):
        for j in range(cols_B):
            s = 0
            for k in range(cols_A):
                s += A[i][k] * B[k][j]
            C[i][j] = s
    return C

def matrix_transpose(A):
    """Транспонирование матрицы."""
    rows, cols = len(A), len(A[0])
    T = [[0] * rows for _ in range(cols)]
    for i in range(rows):
        for j in range(cols):
            T[j][i] = A[i][j]
    return T

# ==========================================
# ЗАДАЧА 2: Класс для операций
# ==========================================

class MatrixOps:
    """Класс-обертка над функциями."""
    @staticmethod
    def add(A, B): return matrix_add(A, B)
    
    @staticmethod
    def scalar_mul(A, scalar): return matrix_scalar_mul(A, scalar)
    
    @staticmethod
    def elementwise_mul(A, B): return matrix_elementwise_mul(A, B)
    
    @staticmethod
    def dot(A, B): return matrix_dot(A, B)
    
    @staticmethod
    def transpose(A): return matrix_transpose(A)

# ==========================================
# ЗАДАЧА 3 и ПРОВЕРКА: Запуск и сравнение
# ==========================================

if __name__ == "__main__":
    print("=== 1. Проверка на примерах из задания ===")
    A_ex = [[2, -1], [3, 0], [-5, 4]]
    B_ex = [[3, 4], [7, -2], [1, 6]]
    print("Сложение:\n", MatrixOps.add(A_ex, B_ex))
    
    M_ex = [[2, -3, 1], [5, 0, 4]]
    print("Умножение на 3:\n", MatrixOps.scalar_mul(M_ex, 3))
    
    print("Поэлементное умножение:\n", MatrixOps.elementwise_mul(A_ex, B_ex))
    
    A2 = [[2, 1], [3, 4]]
    B2 = [[1, 0, 3], [4, 2, 1]]
    print("Скалярное произведение:\n", MatrixOps.dot(A2, B2))
    
    A3 = [[2, 1], [5, 3], [4, 7]]
    print("Транспонирование:\n", MatrixOps.transpose(A3))
    
    print("\n=== 2. Замер времени на матрицах 9x11 ===")
    rows, cols = 9, 11
    A_np = np.random.randint(0, 10, size=(rows, cols))
    B_np = np.random.randint(0, 10, size=(rows, cols))
    B_dot_np = np.random.randint(0, 10, size=(cols, 7))
    
    A_list = A_np.tolist()
    B_list = B_np.tolist()
    B_dot_list = B_dot_np.tolist()
    
    print(f"A_list = \n{A_list}\n B_list = \n{B_list}\n B_dot_list = \n{B_dot_list}\n")
    
    # Замер наших функций
    start = time.perf_counter()
    res_add_my = MatrixOps.add(A_list, B_list)
    time_add_my = time.perf_counter() - start
    
    start = time.perf_counter()
    res_scalar_my = MatrixOps.scalar_mul(A_list, 3)
    time_scalar_my = time.perf_counter() - start
    
    start = time.perf_counter()
    res_elem_my = MatrixOps.elementwise_mul(A_list, B_list)
    time_elem_my = time.perf_counter() - start
    
    start = time.perf_counter()
    res_dot_my = MatrixOps.dot(A_list, B_dot_list)
    time_dot_my = time.perf_counter() - start
    
    start = time.perf_counter()
    res_T_my = MatrixOps.transpose(A_list)
    time_T_my = time.perf_counter() - start
    
    # Замер NumPy
    start = time.perf_counter()
    res_add_np = A_np + B_np
    time_add_np = time.perf_counter() - start
    
    start = time.perf_counter()
    res_scalar_np = A_np * 3
    time_scalar_np = time.perf_counter() - start
    
    start = time.perf_counter()
    res_elem_np = A_np * B_np
    time_elem_np = time.perf_counter() - start
    
    start = time.perf_counter()
    res_dot_np = np.dot(A_np, B_dot_np)
    time_dot_np = time.perf_counter() - start
    
    start = time.perf_counter()
    res_T_np = A_np.T
    time_T_np = time.perf_counter() - start
    
    # Проверка совпадения
    print("Совпадение сложения:", np.array_equal(np.array(res_add_my), res_add_np))
    print("Совпадение умножения на число:", np.array_equal(np.array(res_scalar_my), res_scalar_np))
    print("Совпадение поэлементного умножения:", np.array_equal(np.array(res_elem_my), res_elem_np))
    print("Совпадение скалярного произведения:", np.array_equal(np.array(res_dot_my), res_dot_np))
    print("Совпадение транспонирования:", np.array_equal(np.array(res_T_my), res_T_np))
    
    print("\n--- Время (в секундах) ---")
    print(f"Сложение: свои {time_add_my:.6f} | numpy {time_add_np:.6f}")
    print(f"Умножение на число: свои {time_scalar_my:.6f} | numpy {time_scalar_np:.6f}")
    print(f"Поэлементное умножение: свои {time_elem_my:.6f} | numpy {time_elem_np:.6f}")
    print(f"Скалярное произведение: свои {time_dot_my:.6f} | numpy {time_dot_np:.6f}")
    print(f"Транспонирование: свои {time_T_my:.6f} | numpy {time_T_np:.6f}")