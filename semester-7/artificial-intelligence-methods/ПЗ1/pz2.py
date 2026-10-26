import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Загрузка датасета
df = pd.read_csv("agaricus-lepiota3.csv")

# Разделение признаков и целевого столбца
X = df.drop(columns=["class"]).to_numpy(dtype=np.float64)
y = df["class"].to_numpy(dtype=np.float64).reshape(-1, 1)

print("Размер датасета:", X.shape)
print("Размер целевого столбца:", y.shape)

class MLP:
    def __init__(self, input_size, hidden_size, output_size, use_bias=True):
        self.use_bias = use_bias

        # Веса между входным и скрытым слоями
        self.W1 = np.random.randn(input_size, hidden_size) * np.sqrt(2 / input_size)

        # Веса между скрытым и выходным слоями
        self.W2 = np.random.randn(hidden_size, output_size) * np.sqrt(2 / hidden_size)

        # Смещения
        if self.use_bias:
            self.b1 = np.zeros((1, hidden_size))
            self.b2 = np.zeros((1, output_size))
        else:
            self.b1 = None
            self.b2 = None

    @staticmethod
    def sigmoid(x):
        x = np.clip(x, -500, 500)
        return 1 / (1 + np.exp(-x))

    def forward(self, X):
        # Входной слой -> скрытый слой
        z1 = X @ self.W1

        if self.use_bias:
            z1 += self.b1

        self.a1 = np.maximum(0, z1)  # ReLU

        # Скрытый слой -> выходной слой
        z2 = self.a1 @ self.W2

        if self.use_bias:
            z2 += self.b2

        self.a2 = self.sigmoid(z2)

        return self.a2

    def train(self, X, y, epochs=100, learning_rate=0.01):
        n = X.shape[0]

        for epoch in range(epochs):
            # Прямой проход
            predictions = self.forward(X)

            # Ошибка на выходе (сигмоида + бинарная кросс-энтропия)
            dz2 = predictions - y

            # Градиенты весов второго слоя и смещения
            dW2 = self.a1.T @ dz2 / n

            if self.use_bias:
                db2 = np.mean(dz2, axis=0, keepdims=True)

            # Распространяем ошибку на скрытый слой
            da1 = dz2 @ self.W2.T
            dz1 = da1 * (self.a1 > 0)

            # Градиенты весов первого слоя и смещения
            dW1 = X.T @ dz1 / n

            if self.use_bias:
                db1 = np.mean(dz1, axis=0, keepdims=True)

            # Обновляем веса
            self.W2 -= learning_rate * dW2
            self.W1 -= learning_rate * dW1

            # Обновляем смещения, только если они включены
            if self.use_bias:
                self.b2 -= learning_rate * db2
                self.b1 -= learning_rate * db1

# Разделение данных на обучающую и тестовую выборки
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("Обучающая выборка:", X_train.shape)
print("Тестовая выборка:", X_test.shape)

# Создание и обучение нейросети со смещением
np.random.seed(42)

mlp_bias = MLP(
    input_size=X_train.shape[1],
    hidden_size=16,
    output_size=1,
    use_bias=True
)

mlp_bias.train(X_train, y_train, epochs=100, learning_rate=0.01)

# Предсказание классов на тестовой выборке
y_pred_prob = mlp_bias.forward(X_test)
y_pred = (y_pred_prob >= 0.5).astype(int)

# Оценка точности
accuracy = accuracy_score(y_test, y_pred)

print("\nРезультаты MLP с bias:")
print(f"Точность: {accuracy:.4f} ({accuracy * 100:.2f}%)")

# Создание и обучение нейросети без смещения
np.random.seed(42)

mlp_no_bias = MLP(
    input_size=X_train.shape[1],
    hidden_size=16,
    output_size=1,
    use_bias=False
)

mlp_no_bias.train(X_train, y_train, epochs=100, learning_rate=0.01)

# Предсказание классов на тестовой выборке
y_pred_prob_no_bias = mlp_no_bias.forward(X_test)
y_pred_no_bias = (y_pred_prob_no_bias >= 0.5).astype(int)

# Оценка точности
accuracy_no_bias = accuracy_score(y_test, y_pred_no_bias)

print("\nРезультаты MLP без bias:")
print(f"Точность: {accuracy_no_bias:.4f} ({accuracy_no_bias * 100:.2f}%)")

difference = (accuracy - accuracy_no_bias) * 100

print("\nСравнение моделей:")
print(f"MLP с bias:    {accuracy * 100:.2f}%")
print(f"MLP без bias:  {accuracy_no_bias * 100:.2f}%")
print(f"Разница:       {difference:.2f} процентного пункта")

if difference > 0:
    print("В этом эксперименте модель с bias показала лучший результат.")
elif difference < 0:
    print("В этом эксперименте модель без bias показала лучший результат.")
else:
    print("В этом эксперименте обе модели показали одинаковую точность.")