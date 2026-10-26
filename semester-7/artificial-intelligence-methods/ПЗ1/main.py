import pandas as pd

columns = [
    "class", "cap-shape", "cap-surface", "cap-color", "bruises",
    "odor", "gill-attachment", "gill-spacing", "gill-size",
    "gill-color", "stalk-shape", "stalk-root", "stalk-surface-above-ring",
    "stalk-surface-below-ring", "stalk-color-above-ring",
    "stalk-color-below-ring", "veil-type", "veil-color",
    "ring-number", "ring-type", "spore-print-color",
    "population", "habitat"
]

df = pd.read_csv("data/agaricus-lepiota.data", header=None, names=columns)

print("Размер датасета:", df.shape)
print(df.head())
df.to_csv("agaricus-lepiota.csv", index=False)
print("Таблица сохранена")
constant_columns = [
    col for col in df.columns
    if df[col].nunique() == 1
]

print("Столбцы с постоянными значениями:", constant_columns)
df = df.drop(columns=constant_columns)

print("Размер после удаления постоянных столбцов:", df.shape)

df.to_csv("agaricus-lepiota2.csv", index=False)
print("Обработанная таблица сохранена")
df = df.replace("?", "0")

print("Количество пропущенных значений:")
print((df == "?").sum().sum())

df.to_csv("agaricus-lepiota2.csv", index=False)
print("Данные без знаков пропуска сохранены")
from sklearn.preprocessing import LabelEncoder

for col in df.columns:
    encoder = LabelEncoder()
    df[col] = encoder.fit_transform(df[col])

df.to_csv("agaricus-lepiota3.csv", index=False)

print("Размер итоговой таблицы:", df.shape)
print("Итоговая таблица сохранена")
print(df.head())
print("Уникальные значения класса:", df["class"].unique())