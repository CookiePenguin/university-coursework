import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import load_iris
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from scipy.stats import f as f_dist
from scipy.spatial.distance import mahalanobis
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os
import warnings
warnings.filterwarnings('ignore')

# Настройка стиля графиков
sns.set_theme(style="whitegrid")
plt.rcParams['figure.dpi'] = 150

print("Загрузка данных...")
iris = load_iris()
df = pd.DataFrame(data=iris.data, columns=['Sepallen', 'Sepalwid', 'Petallen', 'Petalwid'])
df['Iristype'] = iris.target + 1 # 1: Setosa, 2: Versicol, 3: Virginic
df['Species'] = df['Iristype'].map({1: 'Setosa', 2: 'Versicol', 3: 'Virginic'})

X = df[['Sepallen', 'Sepalwid', 'Petallen', 'Petalwid']].values
y = df['Iristype'].values
features = ['Sepallen', 'Sepalwid', 'Petallen', 'Petalwid']

doc = Document()
doc.add_heading('Практическая работа №7\nДискриминантный анализ (Многомерные статистические методы)', 0)
doc.add_paragraph('Цель анализа: изучение дискриминации между тремя типами цветов ирисов (Setosa, Versicol, Virginic), основываясь на четырех измерениях: ширине и длине чашелистиков и лепестков.')

# --- 1. Описательные статистики ---
print("Генерация описательных статистик...")
doc.add_heading('1. Просмотр описательных статистик', level=1)

means = df.groupby('Species')[features].mean().round(3)
counts = df.groupby('Species')[features].count()
stats_table = pd.concat([means, counts.iloc[:, 0].rename('N')], axis=1)

doc.add_paragraph('Средние значения и число наблюдений для каждой совокупности:')
table = doc.add_table(rows=1, cols=5)
table.style = 'Table Grid'
hdr_cells = table.rows[0].cells
for i, col in enumerate(['Тип / Переменная'] + features):
    hdr_cells[i].text = col

for idx, row in stats_table.iterrows():
    row_cells = table.add_row().cells
    row_cells[0].text = str(idx)
    for i, col in enumerate(features):
        row_cells[i+1].text = str(row[col])

# Гистограммы
fig, axes = plt.subplots(2, 2, figsize=(10, 8))
for i, col in enumerate(features):
    ax = axes[i//2, i%2]
    for species in ['Setosa', 'Versicol', 'Virginic']:
        subset = df[df['Species'] == species][col]
        ax.hist(subset, bins=10, alpha=0.6, label=species)
    ax.set_title(f'Гистограмма: {col}')
    ax.legend()
plt.tight_layout()
plt.savefig('histograms.png')
plt.close()
doc.add_paragraph('Гистограммы частот распределения для переменных (по группам):')
doc.add_picture('histograms.png', width=Inches(5.5))

# Диаграммы размаха (Boxplots)
fig, axes = plt.subplots(2, 2, figsize=(10, 8))
for i, col in enumerate(features):
    sns.boxplot(x='Species', y=col, data=df, ax=axes[i//2, i%2], palette='Set2')
    axes[i//2, i%2].set_title(f'Диаграмма размаха: {col}')
plt.tight_layout()
plt.savefig('boxplots.png')
plt.close()
doc.add_paragraph('Категоризированные диаграммы размаха (Среднее/SD):')
doc.add_picture('boxplots.png', width=Inches(5.5))

# Диаграмма рассеяния
fig, ax = plt.subplots(figsize=(8, 6))
sns.scatterplot(x='Sepallen', y='Petallen', hue='Species', style='Species', data=df, s=100, ax=ax)
ax.set_title('Диаграмма рассеяния: Sepallen vs Petallen')
plt.tight_layout()
plt.savefig('scatter.png')
plt.close()
doc.add_paragraph('Диаграмма рассеяния корреляций между переменными Sepallen и Petallen. Видны два "облака" точек, что указывает на хорошую дискриминацию.')
doc.add_picture('scatter.png', width=Inches(4.5))

# --- 2. Пошаговый дискриминантный анализ ---
print("Расчет пошагового анализа...")
doc.add_heading('2. Пошаговый дискриминантный анализ', level=1)

def wilks_lambda(X, y):
    classes = np.unique(y)
    n, p = X.shape
    k = len(classes)
    mean_total = np.mean(X, axis=0)
    W = np.zeros((p, p))
    B = np.zeros((p, p))
    for c in classes:
        X_c = X[y == c]
        n_c = X_c.shape[0]
        mean_c = np.mean(X_c, axis=0)
        W += (n_c - 1) * np.cov(X_c, rowvar=False) if n_c > 1 else np.zeros((p,p))
        B += n_c * np.outer(mean_c - mean_total, mean_c - mean_total)
    T = W + B
    return np.linalg.det(W) / np.linalg.det(T), W, B, n, k, p

def calc_f_to_enter(wilks_val, n, k, p_in_model):
    df1 = k - 1
    df2 = n - k - p_in_model
    if df2 <= 0 or wilks_val == 0: return 0
    f_val = ((1 - wilks_val) / wilks_val) * (df2 / df1)
    return f_val

# Шаг 0
doc.add_heading('Результаты на шаге 0', level=2)
doc.add_paragraph('Ни одной переменной еще не включено в модель. Ниже представлены переменные вне модели, их Лямбда Уилкса, F-включить и Толерантность.')

step0_data = []
for i, feat in enumerate(features):
    X_temp = X[:, i].reshape(-1, 1)
    wl, _, _, n, k, _ = wilks_lambda(X_temp, y)
    f_val = calc_f_to_enter(wl, n, k, 0)
    step0_data.append({'Переменная': feat, 'Лямбда Уилкса': round(wl, 4), 'F-включить': round(f_val, 2), 'Толерантность': 1.0})

df_step0 = pd.DataFrame(step0_data)
table = doc.add_table(rows=1, cols=4)
table.style = 'Table Grid'
for i, col in enumerate(df_step0.columns):
    table.rows[0].cells[i].text = col
for _, row in df_step0.iterrows():
    cells = table.add_row().cells
    for i, val in enumerate(row):
        cells[i].text = str(val)
doc.add_paragraph('Вывод: Наибольшее значение F-включить дает переменная Petallen. Она будет введена в модель первой.')

# Шаги 2 и 4 (итоговая модель)
doc.add_heading('Результаты на шаге 4 (последний шаг)', level=2)
wl_total, W, B, n, k, p = wilks_lambda(X, y)
f_total = calc_f_to_enter(wl_total, n, k, p-1)
doc.add_paragraph(f'Внешне, дискриминация между типами ирисов высоко значима (статистика Уилкса лямбда = {wl_total:.3f}; F = {f_total:.1f}, p < 0.0001).')

# Частичная лямбда Уилкса
doc.add_paragraph('Частичная статистика Уилкса лямбда показывает вклад каждой переменной в общую дискриминацию:')
partial_data = []
for i, feat in enumerate(features):
    cols = [j for j in range(p) if j != i]
    X_reduced = X[:, cols]
    wl_red, _, _, _, _, _ = wilks_lambda(X_reduced, y)
    partial_wl = wl_total / wl_red if wl_red != 0 else 0
    partial_data.append({'Переменная': feat, 'Частичная Лямбда': round(partial_wl, 4)})

df_partial = pd.DataFrame(partial_data).sort_values('Частичная Лямбда')
table = doc.add_table(rows=1, cols=2)
table.style = 'Table Grid'
table.rows[0].cells[0].text = 'Переменная'
table.rows[0].cells[1].text = 'Частичная Лямбда'
for _, row in df_partial.iterrows():
    cells = table.add_row().cells
    cells[0].text = row['Переменная']
    cells[1].text = str(row['Частичная Лямбда'])
doc.add_paragraph('Вывод: Переменная Petallen дает вклад больше всех, Petalwid - вторая, Sepalwid - третья, Sepallen - меньше всех. Размеры лепестков являются главными переменными для дискриминации.')

# --- 3. Канонический анализ ---
print("Выполнение канонического анализа...")
doc.add_heading('3. Канонический анализ', level=1)

lda = LDA(n_components=2)
X_lda = lda.fit_transform(X, y)

eigenvalues = lda.explained_variance_ratio_
doc.add_heading('Собственные значения', level=2)
table = doc.add_table(rows=1, cols=3)
table.style = 'Table Grid'
hdr = table.rows[0].cells
hdr[0].text = 'Корень'
hdr[1].text = 'Собственное значение (доля)'
hdr[2].text = 'Накопленная доля'
cumsum = 0
for i, ev in enumerate(eigenvalues):
    cumsum += ev
    cells = table.add_row().cells
    cells[0].text = f'Корень {i+1}'
    cells[1].text = f'{ev:.4f} ({ev*100:.1f}%)'
    cells[2].text = f'{cumsum:.4f}'
doc.add_paragraph('Первая функция ответственна за ~99% объясненной дисперсии, следовательно, она наиболее важна.')

doc.add_heading('Коэффициенты для канонических переменных (Стандартизованные)', level=2)
# Приближенные стандартизованные коэффициенты
scaler_std = np.std(X, axis=0)
std_coefs = lda.scalings_ * scaler_std.reshape(-1, 1)

table = doc.add_table(rows=1, cols=3)
table.style = 'Table Grid'
table.rows[0].cells[0].text = 'Переменная'
table.rows[0].cells[1].text = 'Корень 1'
table.rows[0].cells[2].text = 'Корень 2'
for i, feat in enumerate(features):
    cells = table.add_row().cells
    cells[0].text = feat
    cells[1].text = f'{std_coefs[i, 0]:.4f}'
    cells[2].text = f'{std_coefs[i, 1]:.4f}'
doc.add_paragraph('Первая функция взвешивается наиболее тяжело шириной и длиной лепестков. Вторая функция отмечена главным образом переменной Sepalwid.')

doc.add_heading('Средние канонических переменных', level=2)
means_lda = pd.DataFrame(X_lda, columns=['Root 1', 'Root 2'])
means_lda['Species'] = df['Species']
canon_means = means_lda.groupby('Species').mean().round(3)

table = doc.add_table(rows=1, cols=3)
table.style = 'Table Grid'
table.rows[0].cells[0].text = 'Тип'
table.rows[0].cells[1].text = 'Root 1'
table.rows[0].cells[2].text = 'Root 2'
for sp, row in canon_means.iterrows():
    cells = table.add_row().cells
    cells[0].text = sp
    cells[1].text = str(row['Root 1'])
    cells[2].text = str(row['Root 2'])
doc.add_paragraph('Очевидно, что первая функция отделяет сорт Setosa от других сортов. Вторая функция предназначена для разделения сорта Versicol и других.')

# График канонических корней
fig, ax = plt.subplots(figsize=(8, 6))
sns.scatterplot(x='Root 1', y='Root 2', hue='Species', style='Species', data=means_lda, s=100, ax=ax)
ax.set_title('Диаграмма рассеяния для канонических значений (Корень 1 vs Корень 2)')
plt.tight_layout()
plt.savefig('canonical_scatter.png')
plt.close()
doc.add_paragraph('Диаграмма подтверждает интерпретацию: Setosa далеко справа, Versicol преимущественно имеет негативные значения второй функции.')
doc.add_picture('canonical_scatter.png', width=Inches(4.5))

# --- 4. Классификация ---
print("Расчет классификации...")
doc.add_heading('4. Классификация', level=1)

y_pred = lda.predict(X)
conf_matrix = pd.crosstab(df['Species'], pd.Series(y_pred).map({1:'Setosa', 2:'Versicol', 3:'Virginic'}), rownames=['Истинный'], colnames=['Предсказанный'])

doc.add_heading('Матрица классификации', level=2)
doc.add_paragraph('Априорные вероятности пропорциональны размерам групп (по 1/3 для каждого типа).')
table = doc.add_table(rows=1, cols=4)
table.style = 'Table Grid'
for i, col in enumerate(['Истинный \ Предсказанный'] + list(conf_matrix.columns)):
    table.rows[0].cells[i].text = col
for idx, row in conf_matrix.iterrows():
    cells = table.add_row().cells
    cells[0].text = idx
    for i, val in enumerate(row):
        cells[i+1].text = str(val)

total_correct = np.trace(conf_matrix.values)
total = conf_matrix.values.sum()
accuracy = total_correct / total * 100
doc.add_paragraph(f'Процент правильно классифицированных наблюдений: {accuracy:.2f}%')

doc.add_heading('Расстояния Махаланобиса (первые 5 наблюдений как пример)', level=2)
doc.add_paragraph('Расстояние вычисляется до центроида каждой группы. Чем меньше расстояние, тем выше вероятность принадлежности к группе.')

class_means = lda.means_
cov_pooled = np.cov(X.T) # Общая ковариационная матрица (упрощенно)
inv_cov = np.linalg.inv(cov_pooled)

mah_data = []
for i in range(5):
    d1 = mahalanobis(X[i], class_means[0], inv_cov)
    d2 = mahalanobis(X[i], class_means[1], inv_cov)
    d3 = mahalanobis(X[i], class_means[2], inv_cov)
    mah_data.append({'№ набл.': i+1, 'До Setosa': round(d1**2, 2), 'До Versicol': round(d2**2, 2), 'До Virginic': round(d3**2, 2), 'Истинный класс': df['Species'].iloc[i]})

df_mah = pd.DataFrame(mah_data)
table = doc.add_table(rows=1, cols=5)
table.style = 'Table Grid'
for i, col in enumerate(df_mah.columns):
    table.rows[0].cells[i].text = col
for _, row in df_mah.iterrows():
    cells = table.add_row().cells
    for i, val in enumerate(row):
        cells[i].text = str(val)

doc.add_heading('Итог', level=1)
doc.add_paragraph('Этот пример иллюстрирует основную идею анализа дискриминантных функций. Наиболее значимая и ясная дискриминация возможна для цветов сорта Setosa с использованием первой дискриминантной функции. Точность апостериорной классификации очень высока (около 98%), однако при классификации новых образцов следует ожидать несколько меньшей точности. Если целью является корректная классификация неизвестных образцов, следует провести исследование в два этапа: сначала построить функции классификации и затем провести оценку их качества на тестовой выборке.')

# Сохранение
output_filename = 'PR7_Report.docx'
doc.save(output_filename)
print(f"\n✅ ГОТОВО! Отчет успешно сохранен в файл: {os.path.abspath(output_filename)}")