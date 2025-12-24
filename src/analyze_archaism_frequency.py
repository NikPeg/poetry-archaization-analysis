#!/usr/bin/env python3
"""
Анализ частотности архаизмов по периодам (десятилетиям).
- Подсчёт употреблений архаизмов по десятилетиям
- Вычисление относительной частотности (на 1000 слов)
- Построение графиков динамики
"""

import pandas as pd
import numpy as np
import re
from pathlib import Path
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
import seaborn as sns

# Настройка matplotlib для русского языка
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False


def load_data():
    """Загружает стихотворения и словарь архаизмов."""
    project_root = Path(__file__).parent.parent
    
    print("Загружаю данные...")
    poems_df = pd.read_parquet(project_root / 'dataset' / 'poems.parquet')
    print(f"✓ Стихотворений: {len(poems_df)}")
    
    # Загружаем множество архаизмов
    wordlist_path = project_root / 'dataset' / 'archaisms_wordlist.txt'
    with open(wordlist_path, 'r', encoding='utf-8') as f:
        archaisms = set(line.strip().lower() for line in f if line.strip())
    print(f"✓ Архаизмов в словаре: {len(archaisms)}\n")
    
    return poems_df, archaisms


def tokenize_text(text):
    """Токенизация текста - извлечение русских слов."""
    if not text or not isinstance(text, str):
        return []
    words = re.findall(r'\b[а-яёА-ЯЁ]+\b', text.lower())
    return words


def calculate_decade_statistics(poems_df, archaisms_set):
    """
    Вычисляет статистику по десятилетиям.
    
    Returns:
        DataFrame с колонками: decade, total_words, archaism_count, 
                              archaisms_per_1000, poem_count
    """
    print("Анализирую частотность по десятилетиям...")
    
    # Фильтруем стихи с известным годом
    df = poems_df[poems_df['year'].notna()].copy()
    
    # Вычисляем десятилетие
    df['decade'] = (df['year'] // 10) * 10
    
    stats = []
    
    for decade in sorted(df['decade'].unique()):
        decade_poems = df[df['decade'] == decade]
        
        total_words = 0
        total_archaisms = 0
        
        for text in decade_poems['text']:
            words = tokenize_text(text)
            total_words += len(words)
            
            # Считаем архаизмы
            archaisms_found = sum(1 for w in words if w in archaisms_set)
            total_archaisms += archaisms_found
        
        # Вычисляем частотность на 1000 слов
        archaisms_per_1000 = (total_archaisms / total_words * 1000) if total_words > 0 else 0
        
        stats.append({
            'decade': int(decade),
            'poem_count': len(decade_poems),
            'total_words': total_words,
            'archaism_count': total_archaisms,
            'archaisms_per_1000': archaisms_per_1000
        })
        
        print(f"  {int(decade)}s: {len(decade_poems)} стихов, "
              f"{total_archaisms} архаизмов, "
              f"{archaisms_per_1000:.2f} на 1000 слов")
    
    return pd.DataFrame(stats)


def analyze_by_author(poems_df, archaisms_set, top_n=10):
    """Анализирует использование архаизмов по авторам."""
    print(f"\nАнализирую топ-{top_n} авторов...")
    
    # Берём топ авторов по количеству стихотворений
    top_authors = poems_df['author'].value_counts().head(top_n).index
    
    author_stats = []
    
    for author in top_authors:
        author_poems = poems_df[poems_df['author'] == author]
        
        total_words = 0
        total_archaisms = 0
        
        for text in author_poems['text']:
            words = tokenize_text(text)
            total_words += len(words)
            total_archaisms += sum(1 for w in words if w in archaisms_set)
        
        archaisms_per_1000 = (total_archaisms / total_words * 1000) if total_words > 0 else 0
        
        # Определяем основной период творчества
        years = author_poems['year'].dropna()
        avg_year = int(years.mean()) if len(years) > 0 else None
        
        author_stats.append({
            'author': author,
            'poem_count': len(author_poems),
            'total_words': total_words,
            'archaism_count': total_archaisms,
            'archaisms_per_1000': archaisms_per_1000,
            'avg_year': avg_year
        })
        
        print(f"  {author}: {archaisms_per_1000:.2f} архаизмов на 1000 слов")
    
    return pd.DataFrame(author_stats)


def plot_decade_dynamics(stats_df, output_path):
    """Строит график динамики частотности архаизмов по десятилетиям."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # График 1: Частотность архаизмов на 1000 слов
    ax1.plot(stats_df['decade'], stats_df['archaisms_per_1000'], 
             marker='o', linewidth=2, markersize=6, color='#2E86AB')
    ax1.fill_between(stats_df['decade'], stats_df['archaisms_per_1000'], 
                      alpha=0.3, color='#2E86AB')
    ax1.set_xlabel('Десятилетие', fontsize=12)
    ax1.set_ylabel('Архаизмов на 1000 слов', fontsize=12)
    ax1.set_title('Динамика использования архаизмов в русской поэзии (1720-2000)', 
                  fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(stats_df['decade'].min() - 5, stats_df['decade'].max() + 5)
    
    # Добавляем аннотации для пиковых значений
    max_idx = stats_df['archaisms_per_1000'].idxmax()
    max_decade = stats_df.loc[max_idx, 'decade']
    max_value = stats_df.loc[max_idx, 'archaisms_per_1000']
    ax1.annotate(f'Пик: {max_value:.2f}', 
                xy=(max_decade, max_value),
                xytext=(max_decade + 20, max_value + 0.5),
                arrowprops=dict(arrowstyle='->', color='red', lw=1.5),
                fontsize=10, color='red', fontweight='bold')
    
    # График 2: Количество стихотворений и абсолютное количество архаизмов
    ax2_twin = ax2.twinx()
    
    bars = ax2.bar(stats_df['decade'], stats_df['poem_count'], 
                   width=8, alpha=0.6, color='#A23B72', label='Количество стихотворений')
    ax2.set_xlabel('Десятилетие', fontsize=12)
    ax2.set_ylabel('Количество стихотворений', fontsize=12, color='#A23B72')
    ax2.tick_params(axis='y', labelcolor='#A23B72')
    
    line = ax2_twin.plot(stats_df['decade'], stats_df['archaism_count'], 
                         marker='s', linewidth=2, markersize=6, 
                         color='#F18F01', label='Архаизмы (абсолютное)')
    ax2_twin.set_ylabel('Количество архаизмов', fontsize=12, color='#F18F01')
    ax2_twin.tick_params(axis='y', labelcolor='#F18F01')
    
    ax2.set_title('Объём корпуса и абсолютное количество архаизмов', 
                  fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='x')
    
    # Легенда
    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ График сохранён: {output_path}")


def plot_author_comparison(author_df, output_path):
    """Строит график сравнения авторов по использованию архаизмов."""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Сортируем по частотности
    author_df_sorted = author_df.sort_values('archaisms_per_1000', ascending=True)
    
    # Создаём горизонтальную столбчатую диаграмму
    bars = ax.barh(range(len(author_df_sorted)), 
                   author_df_sorted['archaisms_per_1000'],
                   color=plt.cm.viridis(np.linspace(0.3, 0.9, len(author_df_sorted))))
    
    ax.set_yticks(range(len(author_df_sorted)))
    ax.set_yticklabels(author_df_sorted['author'], fontsize=11)
    ax.set_xlabel('Архаизмов на 1000 слов', fontsize=12)
    ax.set_title('Использование архаизмов авторами (топ-10 по количеству стихотворений)', 
                 fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    
    # Добавляем значения на столбцы
    for i, (bar, row) in enumerate(zip(bars, author_df_sorted.itertuples())):
        width = bar.get_width()
        ax.text(width + 0.05, bar.get_y() + bar.get_height()/2,
                f'{width:.2f}',
                ha='left', va='center', fontsize=9)
        
        # Добавляем период творчества
        if row.avg_year:
            ax.text(0.05, bar.get_y() + bar.get_height()/2,
                    f'~{int(row.avg_year)}',
                    ha='left', va='center', fontsize=8, 
                    color='white', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ График сохранён: {output_path}")


def plot_century_comparison(stats_df, output_path):
    """Строит график сравнения веков."""
    # Группируем по векам
    stats_df_copy = stats_df.copy()
    stats_df_copy['century'] = (stats_df_copy['decade'] // 100) + 1
    
    century_stats = stats_df_copy.groupby('century').agg({
        'total_words': 'sum',
        'archaism_count': 'sum',
        'poem_count': 'sum'
    }).reset_index()
    
    century_stats['archaisms_per_1000'] = (
        century_stats['archaism_count'] / century_stats['total_words'] * 1000
    )
    
    # Фильтруем века с достаточным количеством данных
    century_stats = century_stats[century_stats['poem_count'] >= 50]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x = np.arange(len(century_stats))
    width = 0.6
    
    bars = ax.bar(x, century_stats['archaisms_per_1000'], width,
                  color=['#E63946', '#F77F00', '#06A77D'],
                  edgecolor='black', linewidth=1.5)
    
    ax.set_xlabel('Век', fontsize=12)
    ax.set_ylabel('Архаизмов на 1000 слов', fontsize=12)
    ax.set_title('Сравнение использования архаизмов по векам', 
                 fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([f'{int(c)} век' for c in century_stats['century']], fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Добавляем значения и количество стихотворений
    for i, (bar, row) in enumerate(zip(bars, century_stats.itertuples())):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 0.1,
                f'{height:.2f}',
                ha='center', va='bottom', fontsize=12, fontweight='bold')
        ax.text(bar.get_x() + bar.get_width()/2, height/2,
                f'{row.poem_count} стихов',
                ha='center', va='center', fontsize=9, color='white', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ График сохранён: {output_path}")


def save_statistics_table(stats_df, author_df, output_dir):
    """Сохраняет статистические таблицы в CSV."""
    # Таблица по десятилетиям
    decades_path = output_dir / 'archaism_frequency_by_decade.csv'
    stats_df.to_csv(decades_path, index=False, encoding='utf-8')
    print(f"  ✓ Таблица по десятилетиям: {decades_path}")
    
    # Таблица по авторам
    authors_path = output_dir / 'archaism_frequency_by_author.csv'
    author_df.to_csv(authors_path, index=False, encoding='utf-8')
    print(f"  ✓ Таблица по авторам: {authors_path}")


def main():
    print("="*60)
    print("АНАЛИЗ ЧАСТОТНОСТИ АРХАИЗМОВ ПО ПЕРИОДАМ")
    print("="*60 + "\n")
    
    # Загружаем данные
    poems_df, archaisms_set = load_data()
    
    # Вычисляем статистику по десятилетиям
    print("="*60)
    stats_df = calculate_decade_statistics(poems_df, archaisms_set)
    
    # Анализируем по авторам
    print("="*60)
    author_df = analyze_by_author(poems_df, archaisms_set, top_n=10)
    
    # Создаём визуализации
    print("\n" + "="*60)
    print("СОЗДАНИЕ ВИЗУАЛИЗАЦИЙ")
    print("="*60 + "\n")
    
    results_dir = Path(__file__).parent.parent / 'results'
    results_dir.mkdir(exist_ok=True)
    
    print("Строю графики...")
    plot_decade_dynamics(stats_df, results_dir / 'archaism_dynamics_by_decade.png')
    plot_author_comparison(author_df, results_dir / 'archaism_by_author.png')
    plot_century_comparison(stats_df, results_dir / 'archaism_by_century.png')
    
    # Сохраняем таблицы
    print("\nСохраняю статистические таблицы...")
    save_statistics_table(stats_df, author_df, results_dir)
    
    # Итоговая статистика
    print("\n" + "="*60)
    print("ИТОГОВАЯ СТАТИСТИКА")
    print("="*60)
    
    total_words = stats_df['total_words'].sum()
    total_archaisms = stats_df['archaism_count'].sum()
    overall_frequency = total_archaisms / total_words * 1000
    
    max_decade_idx = stats_df['archaisms_per_1000'].idxmax()
    max_decade = stats_df.loc[max_decade_idx, 'decade']
    max_frequency = stats_df.loc[max_decade_idx, 'archaisms_per_1000']
    
    min_decade_idx = stats_df['archaisms_per_1000'].idxmin()
    min_decade = stats_df.loc[min_decade_idx, 'decade']
    min_frequency = stats_df.loc[min_decade_idx, 'archaisms_per_1000']
    
    print(f"\nОбщая статистика:")
    print(f"  Всего слов в корпусе: {total_words:,}")
    print(f"  Всего архаизмов найдено: {total_archaisms:,}")
    print(f"  Средняя частотность: {overall_frequency:.2f} на 1000 слов")
    
    print(f"\nПериод максимального использования:")
    print(f"  {int(max_decade)}s: {max_frequency:.2f} архаизмов на 1000 слов")
    
    print(f"\nПериод минимального использования:")
    print(f"  {int(min_decade)}s: {min_frequency:.2f} архаизмов на 1000 слов")
    
    print(f"\nАвтор с наибольшим использованием архаизмов:")
    top_author = author_df.loc[author_df['archaisms_per_1000'].idxmax()]
    print(f"  {top_author['author']}: {top_author['archaisms_per_1000']:.2f} на 1000 слов")
    
    print("\n" + "="*60)
    print("✓ АНАЛИЗ ЗАВЕРШЁН")
    print("="*60 + "\n")
    
    print("Созданные файлы:")
    print("  Графики:")
    print("    - archaism_dynamics_by_decade.png")
    print("    - archaism_by_author.png")
    print("    - archaism_by_century.png")
    print("  Таблицы:")
    print("    - archaism_frequency_by_decade.csv")
    print("    - archaism_frequency_by_author.csv")
    print()


if __name__ == '__main__':
    main()

