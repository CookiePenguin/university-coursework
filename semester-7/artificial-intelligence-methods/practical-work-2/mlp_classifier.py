import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import MinMaxScaler

# Фиксируем seed для воспроизводимости результатов
np.random.seed(42)

class MultilayerPerceptron:
    """
    Собственная реализация многослойного персептрона (MLP)
    с поддержкой и без использования смещения (bias term).
    Реализовано с использованием мини-батч градиентного спуска.
    """
    def __init__(self, input_size, hidden_size, output_size, use_bias=True, learning_rate=0.1, epochs=100, batch_size=64):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.use_bias = use_bias
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.batch_size = batch_size
        
        # Инициализация весов по Xavier (Glorot) для стабильного обучения
        self.weights_input_hidden = np.random.randn(self.input_size, self.hidden_size) * np.sqrt(2.0 / (self.input_size + self.hidden_size))
        self.weights_hidden_output = np.random.randn(self.hidden_size, self.output_size) * np.sqrt(2.0 / (self.hidden_size + self.output_size))
        
        # Инициализация смещений (bias), если use_bias=True
        if self.use_bias:
            self.bias_hidden = np.zeros((1, self.hidden_size))
            self.bias_output = np.zeros((1, self.output_size))
        else:
            self.bias_hidden = None
            self.bias_output = None
        
        self.loss_history = []
    
    def sigmoid(self, x):
        """Функция активации: сигмоида с защитой от переполнения"""
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))
    
    def forward(self, X):
        """Прямое распространение (forward pass)"""
        self.hidden_input = np.dot(X, self.weights_input_hidden)
        if self.use_bias:
            self.hidden_input += self.bias_hidden
        self.hidden_output = self.sigmoid(self.hidden_input)
        
        self.final_input = np.dot(self.hidden_output, self.weights_hidden_output)
        if self.use_bias:
            self.final_input += self.bias_output
        self.final_output = self.sigmoid(self.final_input)
        
        return self.final_output
    
    def fit(self, X, y):
        """Обучение модели с использованием мини-батчей"""
        n_samples = X.shape[0]
        
        for epoch in range(self.epochs):
            # Перемешиваем данные перед каждой эпохой
            indices = np.random.permutation(n_samples)
            X_shuffled = X[indices]
            y_shuffled = y[indices]
            
            epoch_loss = 0
            n_batches = 0
            
            for i in range(0, n_samples, self.batch_size):
                X_batch = X_shuffled[i:i+self.batch_size]
                y_batch = y_shuffled[i:i+self.batch_size]
                
                # Прямое распространение
                output = self.forward(X_batch)
                
                # Вычисление ошибки (MSE)
                output_error = y_batch - output
                epoch_loss += np.mean(output_error ** 2)
                n_batches += 1
                
                # Обратное распространение ошибки (Backpropagation)
                output_delta = output_error * output * (1 - output)
                hidden_error = output_delta.dot(self.weights_hidden_output.T)
                hidden_delta = hidden_error * self.hidden_output * (1 - self.hidden_output)
                
                # Обновление весов (делим на batch_size для усреднения градиента)
                self.weights_hidden_output += self.hidden_output.T.dot(output_delta) * (self.learning_rate / self.batch_size)
                self.weights_input_hidden += X_batch.T.dot(hidden_delta) * (self.learning_rate / self.batch_size)
                
                # Обновление смещений (bias)
                if self.use_bias:
                    self.bias_output += np.sum(output_delta, axis=0, keepdims=True) * (self.learning_rate / self.batch_size)
                    self.bias_hidden += np.sum(hidden_delta, axis=0, keepdims=True) * (self.learning_rate / self.batch_size)
            
            avg_loss = epoch_loss / n_batches
            self.loss_history.append(avg_loss)
            
            if (epoch + 1) % 10 == 0:
                print(f"Эпоха {epoch + 1}/{self.epochs}, Потеря: {avg_loss:.4f}")
    
    def predict(self, X):
        """Предсказание классов"""
        output = self.forward(X)
        return np.argmax(output, axis=1)


def load_mushroom_dataset(filepath='agaricus-lepiota3.csv'):
    # 1. Загружаем данные из локального CSV
    df = pd.read_csv(filepath)
    
    # 2. Отделяем целевую переменную (первый столбец 'class') от признаков
    X = df.drop('class', axis=1).values
    y = df['class'].values
    
    # 3. Нормализация Min-Max
    scaler = MinMaxScaler()
    X = scaler.fit_transform(X)
    
    # 4. Разделяем на обучающую и тестовую выборки (80% / 20%)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 5. One-Hot Encoding для правильных ответов (классов)
    def to_one_hot(y_array):
        n_classes = 2
        one_hot = np.zeros((len(y_array), n_classes))
        one_hot[np.arange(len(y_array)), y_array] = 1
        return one_hot

    y_train_onehot = to_one_hot(y_train)
    y_test_onehot = to_one_hot(y_test)
    
    return X_train, X_test, y_train, y_test, y_train_onehot, y_test_onehot


def main():
    X_train, X_test, y_train, y_test, y_train_onehot, y_test_onehot = load_mushroom_dataset()
    
    input_size = X_train.shape[1]
    hidden_size = 20
    output_size = 2
    
    print("\n" + "="*60)
    print("Обучение MLP С использованием смещения (bias)")
    print("="*60)
    mlp_with_bias = MultilayerPerceptron(
        input_size=input_size, hidden_size=hidden_size, output_size=output_size,
        use_bias=True, learning_rate=0.1, epochs=100, batch_size=64
    )
    mlp_with_bias.fit(X_train, y_train_onehot)
    y_pred_with_bias = mlp_with_bias.predict(X_test)
    accuracy_with_bias = accuracy_score(y_test, y_pred_with_bias)
    print(f"\nТочность MLP с bias: {accuracy_with_bias * 100:.2f}%")
    
    print("\n" + "="*60)
    print("Обучение MLP БЕЗ использования смещения (bias)")
    print("="*60)
    mlp_without_bias = MultilayerPerceptron(
        input_size=input_size, hidden_size=hidden_size, output_size=output_size,
        use_bias=False, learning_rate=0.1, epochs=100, batch_size=64
    )
    mlp_without_bias.fit(X_train, y_train_onehot)
    y_pred_without_bias = mlp_without_bias.predict(X_test)
    accuracy_without_bias = accuracy_score(y_test, y_pred_without_bias)
    print(f"\nТочность MLP без bias: {accuracy_without_bias * 100:.2f}%")
    
    # Сравнение результатов
    print("\n" + "="*60)
    print("СРАВНЕНИЕ РЕЗУЛЬТАТОВ")
    print("="*60)
    print(f"MLP с bias:    {accuracy_with_bias * 100:.2f}% (Loss: {mlp_with_bias.loss_history[-1]:.4f})")
    print(f"MLP без bias:  {accuracy_without_bias * 100:.2f}% (Loss: {mlp_without_bias.loss_history[-1]:.4f})")
    print(f"Разница:       {(accuracy_with_bias - accuracy_without_bias) * 100:.2f}%")
    
    # Визуализация
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    models = ['С bias', 'Без bias']
    accuracies = [accuracy_with_bias * 100, accuracy_without_bias * 100]
    colors = ['#2ecc71', '#e74c3c']
    plt.bar(models, accuracies, color=colors, alpha=0.8)
    plt.ylabel('Точность (%)')
    plt.title('Сравнение точности моделей')
    plt.ylim(0, 105)
    for i, v in enumerate(accuracies):
        plt.text(i, v + 2, f'{v:.2f}%', ha='center', fontweight='bold')
    
    plt.subplot(1, 2, 2)
    plt.plot(mlp_with_bias.loss_history, label='С bias', color='#2ecc71', linewidth=2)
    plt.plot(mlp_without_bias.loss_history, label='Без bias', color='#e74c3c', linewidth=2)
    plt.xlabel('Эпоха')
    plt.ylabel('Потеря (MSE)')
    plt.title('История обучения')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('comparison_results.png', dpi=300, bbox_inches='tight')
    print("\n✅ График успешно сохранен в файл: comparison_results.png")

if __name__ == "__main__":
    main()