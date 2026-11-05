import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt
from sklearn.datasets import fetch_openml
from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

def load_and_preprocess_data():
    print("Загрузка Mushroom Data Set...")
    mushroom = fetch_openml(name='mushroom', version=1, as_frame=False, parser='auto')
    
    X = mushroom.data
    y = mushroom.target
    
    X_encoded = np.zeros_like(X, dtype=float)
    for i in range(X.shape[1]):
        le = LabelEncoder()
        X_encoded[:, i] = le.fit_transform(X[:, i])
        
    y_encoder = LabelEncoder()
    y_encoded = y_encoder.fit_transform(y)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X_encoded, y_encoded, test_size=0.2, random_state=42
    )
    return X_train, X_test, y_train, y_test

def evaluate_model(model, X_train, y_train, X_test, y_test, model_name):
    start_train = time.time()
    model.fit(X_train, y_train)
    train_time = time.time() - start_train
    
    start_test = time.time()
    y_pred = model.predict(X_test)
    test_time = time.time() - start_test
    
    metrics = {
        "Модель": model_name,
        "Accuracy": accuracy_score(y_test, y_pred),
        "Precision": precision_score(y_test, y_pred, average='macro', zero_division=0),
        "Recall": recall_score(y_test, y_pred, average='macro', zero_division=0),
        "F1-measure": f1_score(y_test, y_pred, average='macro', zero_division=0),
        "Время обучения (с)": round(train_time, 4),
        "Время теста (с)": round(test_time, 4)
    }
    return metrics

def main():
    X_train, X_test, y_train, y_test = load_and_preprocess_data()
    
    models_config = [
        {"name": "1. Baseline", "params": {}},
        {"name": "2. Два скрытых слоя", "params": {"hidden_layer_sizes": (50, 50)}},
        {"name": "3. Активация Tanh", "params": {"activation": "tanh"}},
        {"name": "4. Активация ReLU", "params": {"activation": "relu"}},
        {"name": "5. Оптимизатор Adam", "params": {"solver": "adam"}},
        {"name": "6. L2-регуляризация (0.01)", "params": {"alpha": 0.01}},
        {"name": "7. Адаптивный темп обучения", "params": {"learning_rate": "adaptive"}},
        {"name": "8. SGD с momentum=0.95", "params": {"solver": "sgd", "momentum": 0.95}},
        {"name": "9. Увеличенный batch_size=256", "params": {"batch_size": 256}},
        {"name": "10. Сложная сеть (ReLU+Adam)", "params": {"hidden_layer_sizes": (100, 50, 25), "activation": "relu", "solver": "adam"}}
    ]
    
    results = []
    print("\n" + "="*60)
    print("ЭКСПЕРИМЕНТ 1: Сравнение 10 конфигураций MLP")
    print("="*60)
    
    for config in models_config:
        print(f"Обучение: {config['name']}...")
        model = MLPClassifier(max_iter=300, random_state=42, **config['params'])
        metrics = evaluate_model(model, X_train, y_train, X_test, y_test, config['name'])
        results.append(metrics)
        
    df_results = pd.DataFrame(results)
    print("\nСводная таблица результатов:")
    print(df_results.to_string(index=False))
    df_results.to_csv("models_comparison.csv", index=False, encoding='utf-8')
    
    print("\n" + "="*60)
    print("ЭКСПЕРИМЕНТ 2: Влияние нормализации данных [0, 1]")
    print("="*60)
    scaler = MinMaxScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model_scaled = MLPClassifier(max_iter=300, random_state=42)
    metrics_scaled = evaluate_model(model_scaled, X_train_scaled, y_train, X_test_scaled, y_test, "11. Baseline + Normalization")
    results.append(metrics_scaled)
    
    print("\n" + "="*60)
    print("ЭКСПЕРИМЕНТ 3: Поиск гиперпараметров")
    print("="*60)
    
    print("Запуск Grid Search...")
    param_grid = {'hidden_layer_sizes': [(50,), (100,)], 'activation': ['logistic', 'relu'], 'solver': ['sgd', 'adam']}
    grid_search = GridSearchCV(MLPClassifier(max_iter=300, random_state=42), param_grid, cv=3, n_jobs=-1)
    grid_search.fit(X_train_scaled, y_train)
    print(f"Лучшие параметры Grid Search: {grid_search.best_params_}")
    
    print("\nЗапуск Random Search...")
    param_dist = {'hidden_layer_sizes': [(50,), (100,), (50, 50)], 'activation': ['logistic', 'tanh', 'relu'], 'alpha': [0.0001, 0.01], 'learning_rate': ['constant', 'adaptive']}
    random_search = RandomizedSearchCV(MLPClassifier(max_iter=300, random_state=42), param_distributions=param_dist, n_iter=5, cv=3, random_state=42, n_jobs=-1)
    random_search.fit(X_train_scaled, y_train)
    print(f"Лучшие параметры Random Search: {random_search.best_params_}")
    
    # === ВИЗУАЛИЗАЦИЯ ===
    print("\nГенерация графика сравнения...")
    df_all = pd.DataFrame(results)
    model_names = [name.split('. ')[1] if '. ' in name else name for name in df_all['Модель']] # Убираем номера для чистоты графика
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 8))
    
    # График 1: Точность
    colors_acc = ['#2ecc71' if acc == 1.0 else '#e74c3c' for acc in df_all['Accuracy']]
    bars1 = ax1.barh(model_names, df_all['Accuracy'] * 100, color=colors_acc, alpha=0.8)
    ax1.set_xlabel('Точность (%)')
    ax1.set_title('Сравнение точности (Accuracy) моделей')
    ax1.set_xlim(90, 101)
    for bar in bars1:
        ax1.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, f"{bar.get_width():.1f}%", va='center', fontsize=9)
    
    # График 2: Время обучения
    colors_time = plt.cm.viridis(np.linspace(0.2, 0.8, len(model_names)))
    bars2 = ax2.barh(model_names, df_all['Время обучения (с)'], color=colors_time, alpha=0.8)
    ax2.set_xlabel('Время обучения (секунды)')
    ax2.set_title('Сравнение времени обучения моделей')
    for bar in bars2:
        ax2.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, f"{bar.get_width():.2f}с", va='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('results_visualization.png', dpi=300, bbox_inches='tight')
    print("✅ График сохранен в файл: results_visualization.png")
    print("✅ Все эксперименты завершены. Результаты сохранены в models_comparison.csv")

if __name__ == "__main__":
    main()