import numpy as np
from scipy.special import expit

# ==========================================
# 1. Подготовка данных (Таблицы истинности)
# ==========================================
X_and = np.matrix([[0, 0], [0, 1], [1, 0], [1, 1]])
Y_and = np.matrix([[0], [0], [0], [1]])

X_or = np.matrix([[0, 0], [0, 1], [1, 0], [1, 1]])
Y_or = np.matrix([[0], [1], [1], [1]])

X_xor = np.matrix([[0, 0], [0, 1], [1, 0], [1, 1]])
Y_xor = np.matrix([[0], [1], [1], [0]])

# ==========================================
# 2. Класс нейронной сети (архитектура 2-2-1)
# ==========================================
class SimpleNeuralNetwork:
    def __init__(self):
        # Веса [-1, 1]
        self.W_ih = np.random.random_sample((2, 2)) * 2 - 1
        self.W_ho = np.random.random_sample((1, 2)) * 2 - 1

        # Атрибуты для матриц
        self.X = None
        self.Y = None
        self.H = None
        self.H_sigmoid = None
        self.O = None
        self.O_sigmoid = None
        self.E_o = None
        self.E_h = None

    def fit(self, X, Y):
        """Сохраняет входные и выходные данные."""
        self.X = np.matrix(X)
        self.Y = np.matrix(Y)

    def train(self):
        """Метод обучения: прямой и обратный проход (расчет всех матриц)."""
        # 1. Прямое распространение (Forward Pass)
        # H = X * W_ih (размер: 4x2 * 2x2 = 4x2)
        self.H = self.X * self.W_ih
        
        # H_sigmoid = сигмоида(H)
        self.H_sigmoid = expit(self.H)

        # O = H_sigmoid * W_ho.T 
        # (W_ho имеет размер 1x2, транспонируем в 2x1, чтобы умножить 4x2 * 2x1 = 4x1)
        self.O = self.H_sigmoid * self.W_ho.T
        
        # O_sigmoid = сигмоида(O) -> это и есть выход сети
        self.O_sigmoid = expit(self.O)

        # 2. Обратное распространение ошибки (Backward Pass)
        # E_o = Y - O_sigmoid (ошибка выхода, размер 4x1)
        self.E_o = self.Y - self.O_sigmoid

        # E_h = E_o * W_ho (распределяем ошибку на скрытый слой, 4x1 * 1x2 = 4x2)
        self.E_h = self.E_o * self.W_ho

    def predict(self, X_new):
        """Метод проверки сети на новых данных (без изменения атрибутов класса)."""
        X_new = np.matrix(X_new)
        
        H = X_new * self.W_ih
        H_sigmoid = expit(H)
        
        O = H_sigmoid * self.W_ho.T
        O_sigmoid = expit(O)
        
        return O_sigmoid

# ==========================================
# 3. Проверка (Запуск)
# ==========================================
if __name__ == "__main__":
    print("=== Инициализация и fit() ===")
    nn = SimpleNeuralNetwork()
    nn.fit(X_xor, Y_xor)
    
    print("\n=== Обучение (1 проход) ===")
    nn.train()
    
    print("Входящие сигналы скрытого слоя (H):\n", nn.H)
    print("Исходящие сигналы скрытого слоя (H_sigmoid):\n", nn.H_sigmoid)
    print("Входящие сигналы выхода (O):\n", nn.O)
    print("Исходящие сигналы выхода / Ответ сети (O_sigmoid):\n", nn.O_sigmoid)
    
    print("\nОшибки выходного слоя (E_o):\n", nn.E_o)
    print("Ошибки скрытого слоя (E_h):\n", nn.E_h)

    print("\n=== Проверка сети (Predict) ===")
    # Проверяем на отдельном примере [1, 1] (для XOR правильный ответ 0)
    print("Предсказание для [1, 1]:\n", nn.predict([[1, 1]]))
    
    # Проверяем на всей таблице сразу
    print("Предсказание для всей таблицы X:\n", nn.predict(X_xor))