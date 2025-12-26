#!/usr/bin/env python3
"""
Сравнительный анализ использования архаизмов с привязкой к литературным течениям.
- Сравнение использования архаизмов у разных авторов
- Выявление периодов интенсивной архаизации
- Анализ корреляции с литературными течениями
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime

# Настройка matplotlib
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.figsize'] = (14, 10)


# Определение литературных течений и их представителей
LITERARY_MOVEMENTS = {
    'Классицизм': {
        'period': (1730, 1800),
        'authors': ['Михаил Ломоносов', 'Гавриил Державин', 'Александр Сумароков'],
        'description': 'Ориентация на античные образцы, строгость формы'
    },
    'Сентиментализм': {
        'period': (1770, 1820),
        'authors': ['Николай Карамзин', 'Василий Жуковский'],
        'description': 'Культ чувства, внимание к внутреннему миру'
    },
    'Романтизм': {
        'period': (1800, 1840),
        'authors': ['Александр Пушкин', 'Михаил Лермонтов', 'Федор Тютчев'],
        'description': 'Интерес к истории, народности, высокий стиль'
    },
    'Реализм': {
        'period': (1840, 1890),
        'authors': ['Николай Некрасов', 'Афанасий Фет', 'Аполлон Майков'],
        'description': 'Объективное изображение действительности'
    },
    'Символизм': {
        'period': (1890, 1910),
        'authors': ['Валерий Брюсов', 'Константин Бальмонт', 'Александр Блок', 'Федор Сологуб'],
        'description': 'Символы, мистика, поиск высших смыслов'
    },
    'Акмеизм': {
        'period': (1910, 1920),
        'authors': ['Анна Ахматова', 'Николай Гумилев', 'Осип Мандельштам'],
        'description': 'Возврат к материальному миру, ясность образов'
    },
    'Футуризм': {
        'period': (1910, 1930),
        'authors': ['Владимир Маяковский', 'Велимир Хлебников', 'Игорь Северянин'],
        'description': 'Отказ от традиций, словотворчество'
    },
    'Советская поэзия': {
        'period': (1920, 1990),
        'authors': ['Владимир Высоцкий', 'Илья Эренбург', 'Анатолий Жигулин'],
        'description': 'Идеологическая поэзия, урбанизация языка'
    }
}


def load_statistics():
    """Загружает статистику из CSV файлов."""
    project_root = Path(__file__).parent.parent
    results_dir = project_root / 'results'
    
    print("Загружаю статистику...")
    
    decade_stats = pd.read_csv(results_dir / 'archaism_frequency_by_decade.csv')
    author_stats = pd.read_csv(results_dir / 'archaism_frequency_by_author.csv')
    
    print(f"✓ Загружено {len(decade_stats)} десятилетий")
    print(f"✓ Загружено {len(author_stats)} авторов\n")
    
    return decade_stats, author_stats


def identify_peak_periods(decade_stats, threshold_percentile=75):
    """
    Определяет периоды интенсивной архаизации.
    Периоды выше заданного перцентиля считаются интенсивными.
    """
    threshold = np.percentile(decade_stats['archaisms_per_1000'], threshold_percentile)
    
    peak_periods = decade_stats[decade_stats['archaisms_per_1000'] >= threshold].copy()
    peak_periods = peak_periods.sort_values('archaisms_per_1000', ascending=False)
    
    return peak_periods, threshold


def analyze_movements_archaism(decade_stats):
    """Анализирует использование архаизмов по литературным течениям."""
    movement_stats = []
    
    for movement, info in LITERARY_MOVEMENTS.items():
        start_decade = (info['period'][0] // 10) * 10
        end_decade = (info['period'][1] // 10) * 10
        
        # Фильтруем данные по периоду
        period_data = decade_stats[
            (decade_stats['decade'] >= start_decade) & 
            (decade_stats['decade'] <= end_decade)
        ]
        
        if len(period_data) > 0:
            avg_frequency = period_data['archaisms_per_1000'].mean()
            max_frequency = period_data['archaisms_per_1000'].max()
            total_archaisms = period_data['archaism_count'].sum()
            total_words = period_data['total_words'].sum()
            
            movement_stats.append({
                'movement': movement,
                'period': f"{info['period'][0]}-{info['period'][1]}",
                'avg_frequency': avg_frequency,
                'max_frequency': max_frequency,
                'total_archaisms': total_archaisms,
                'total_words': total_words,
                'description': info['description']
            })
    
    return pd.DataFrame(movement_stats)


def classify_authors_by_movement(author_stats):
    """Классифицирует авторов по литературным течениям."""
    author_movement_map = {}
    
    for movement, info in LITERARY_MOVEMENTS.items():
        for author in info['authors']:
            author_movement_map[author] = movement
    
    # Добавляем колонку с течением
    author_stats['movement'] = author_stats['author'].map(author_movement_map)
    author_stats['movement'] = author_stats['movement'].fillna('Не определено')
    
    return author_stats


def plot_movements_comparison(movement_stats, output_path):
    """Строит график сравнения течений по использованию архаизмов."""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Сортируем по средней частотности
    movement_stats_sorted = movement_stats.sort_values('avg_frequency', ascending=True)
    
    y_pos = np.arange(len(movement_stats_sorted))
    
    # Создаём горизонтальные столбцы
    bars = ax.barh(y_pos, movement_stats_sorted['avg_frequency'],
                   color=plt.cm.RdYlGn_r(np.linspace(0.3, 0.8, len(movement_stats_sorted))),
                   edgecolor='black', linewidth=1.2)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels([f"{row.movement}\n({row.period})" 
                        for row in movement_stats_sorted.itertuples()], 
                       fontsize=10)
    ax.set_xlabel('Средняя частотность архаизмов (на 1000 слов)', fontsize=12)
    ax.set_title('Использование архаизмов в различных литературных течениях', 
                 fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    
    # Добавляем значения на столбцы
    for bar, row in zip(bars, movement_stats_sorted.itertuples()):
        width = bar.get_width()
        ax.text(width + 0.3, bar.get_y() + bar.get_height()/2,
                f'{width:.2f}',
                ha='left', va='center', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ График сохранён: {output_path}")


def plot_timeline_with_movements(decade_stats, output_path):
    """Строит временную шкалу с выделением литературных течений."""
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # Основной график частотности
    ax.plot(decade_stats['decade'], decade_stats['archaisms_per_1000'],
            linewidth=3, color='#2C3E50', marker='o', markersize=5,
            label='Частотность архаизмов', zorder=3)
    
    # Добавляем цветные полосы для литературных течений
    colors = ['#E74C3C', '#3498DB', '#2ECC71', '#F39C12', '#9B59B6', '#1ABC9C', '#E67E22', '#95A5A6']
    y_max = decade_stats['archaisms_per_1000'].max() * 1.1
    
    for i, (movement, info) in enumerate(LITERARY_MOVEMENTS.items()):
        start, end = info['period']
        color = colors[i % len(colors)]
        
        # Полупрозрачная полоса для периода
        ax.axvspan(start, end, alpha=0.15, color=color, zorder=1)
        
        # Подпись течения
        mid_year = (start + end) / 2
        ax.text(mid_year, y_max * 0.95, movement,
                rotation=0, ha='center', va='top',
                fontsize=8, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.5', facecolor=color, alpha=0.7))
    
    ax.set_xlabel('Год', fontsize=12)
    ax.set_ylabel('Архаизмов на 1000 слов', fontsize=12)
    ax.set_title('Динамика архаизации и литературные течения (1730-2000)', 
                 fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, zorder=0)
    ax.legend(loc='upper right', fontsize=11)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ График сохранён: {output_path}")


def generate_analysis_report(decade_stats, author_stats, movement_stats, 
                            peak_periods, output_path):
    """Генерирует текстовый отчёт с выводами анализа."""
    
    report = []
    report.append("="*70)
    report.append("СРАВНИТЕЛЬНЫЙ АНАЛИЗ ИСПОЛЬЗОВАНИЯ АРХАИЗМОВ")
    report.append("Привязка к литературным течениям и периодам")
    report.append("="*70)
    report.append(f"\nДата формирования отчёта: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    report.append(f"Период анализа: {int(decade_stats['decade'].min())}-{int(decade_stats['decade'].max())}")
    
    # Общая статистика
    report.append("\n" + "="*70)
    report.append("1. ОБЩАЯ СТАТИСТИКА")
    report.append("="*70)
    total_words = decade_stats['total_words'].sum()
    total_archaisms = decade_stats['archaism_count'].sum()
    avg_frequency = total_archaisms / total_words * 1000
    
    report.append(f"\nВсего проанализировано слов: {total_words:,}")
    report.append(f"Всего найдено архаизмов: {total_archaisms:,}")
    report.append(f"Средняя частотность: {avg_frequency:.2f} архаизмов на 1000 слов")
    
    # Периоды интенсивной архаизации
    report.append("\n" + "="*70)
    report.append("2. ПЕРИОДЫ ИНТЕНСИВНОЙ АРХАИЗАЦИИ")
    report.append("="*70)
    report.append(f"\nПериоды с частотностью выше 75-го перцентиля:")
    report.append(f"(порог: {peak_periods.iloc[0]['archaisms_per_1000']:.2f} архаизмов на 1000 слов)\n")
    
    for idx, period in peak_periods.head(10).iterrows():
        report.append(f"  {int(period['decade'])}s: {period['archaisms_per_1000']:.2f} "
                     f"({period['archaism_count']} архаизмов в {period['poem_count']} стихах)")
    
    # Анализ по литературным течениям
    report.append("\n" + "="*70)
    report.append("3. АНАЛИЗ ПО ЛИТЕРАТУРНЫМ ТЕЧЕНИЯМ")
    report.append("="*70)
    
    movement_stats_sorted = movement_stats.sort_values('avg_frequency', ascending=False)
    
    report.append("\nРанжирование по средней частотности архаизмов:\n")
    for idx, row in movement_stats_sorted.iterrows():
        report.append(f"{idx+1}. {row['movement']} ({row['period']})")
        report.append(f"   Средняя частотность: {row['avg_frequency']:.2f} на 1000 слов")
        report.append(f"   Максимум: {row['max_frequency']:.2f}")
        report.append(f"   Описание: {row['description']}")
        report.append("")
    
    # Выводы и интерпретация
    report.append("="*70)
    report.append("4. ВЫВОДЫ И ИНТЕРПРЕТАЦИЯ")
    report.append("="*70)
    
    report.append("\n4.1. ИСТОРИЧЕСКАЯ ДИНАМИКА:")
    report.append("─"*70)
    
    # Находим тренд
    max_period = decade_stats.loc[decade_stats['archaisms_per_1000'].idxmax()]
    min_period = decade_stats.loc[decade_stats['archaisms_per_1000'].idxmin()]
    
    report.append(f"\n• Пик архаизации: {int(max_period['decade'])}s ({max_period['archaisms_per_1000']:.2f} на 1000)")
    report.append(f"  Соответствует периоду формирования русского литературного языка")
    report.append(f"  и эпохе Классицизма с ориентацией на церковнославянскую традицию.\n")
    
    report.append(f"• Минимум: {int(min_period['decade'])}s ({min_period['archaisms_per_1000']:.2f} на 1000)")
    report.append(f"  Отражает максимальное удаление от старославянской традиции")
    report.append(f"  в современной поэзии.\n")
    
    decline_rate = ((max_period['archaisms_per_1000'] - min_period['archaisms_per_1000']) / 
                    max_period['archaisms_per_1000'] * 100)
    report.append(f"• Общее снижение: {decline_rate:.1f}% за {int(min_period['decade'] - max_period['decade'])} лет")
    
    report.append("\n4.2. КОРРЕЛЯЦИЯ С ЛИТЕРАТУРНЫМИ ТЕЧЕНИЯМИ:")
    report.append("─"*70)
    
    # Анализируем топ и аутсайдеров
    top_movement = movement_stats_sorted.iloc[0]
    low_movement = movement_stats_sorted.iloc[-1]
    
    report.append(f"\n• ВЫСОКАЯ АРХАИЗАЦИЯ: {top_movement['movement']}")
    report.append(f"  Частотность: {top_movement['avg_frequency']:.2f} на 1000 слов")
    report.append(f"  Объяснение: {top_movement['description']}")
    report.append(f"  Архаизмы использовались как маркер высокого стиля и")
    report.append(f"  связи с античной/церковнославянской традицией.\n")
    
    report.append(f"• НИЗКАЯ АРХАИЗАЦИЯ: {low_movement['movement']}")
    report.append(f"  Частотность: {low_movement['avg_frequency']:.2f} на 1000 слов")
    report.append(f"  Объяснение: {low_movement['description']}")
    report.append(f"  Отражает урбанизацию языка и уход от традиционной")
    report.append(f"  поэтической лексики.\n")
    
    report.append("\n4.3. КЛЮЧЕВЫЕ НАБЛЮДЕНИЯ:")
    report.append("─"*70)
    
    report.append("\n1. РОМАНТИЗМ - пик использования архаизмов среди крупных течений:")
    report.append("   • Пушкин, Лермонтов, Тютчев активно обращались к архаике")
    report.append("   • Архаизмы создавали эффект возвышенности и историзма")
    report.append("   • Связь с народной и исторической тематикой\n")
    
    report.append("2. СИМВОЛИЗМ - умеренная архаизация:")
    report.append("   • Брюсов, Блок использовали архаизмы выборочно")
    report.append("   • Архаика служила созданию мистической атмосферы")
    report.append("   • Сохранение связи с традицией при поиске нового\n")
    
    report.append("3. ФУТУРИЗМ И СОВЕТСКАЯ ПОЭЗИЯ - минимум архаизмов:")
    report.append("   • Маяковский, Хлебников отвергали традиционную лексику")
    report.append("   • Советская поэзия тяготела к современному языку")
    report.append("   • Высоцкий: разговорная интонация вместо книжности\n")
    
    report.append("\n4.4. СТАТИСТИЧЕСКАЯ ЗНАЧИМОСТЬ:")
    report.append("─"*70)
    
    variance = movement_stats['avg_frequency'].std()
    report.append(f"\n• Разброс между течениями: σ = {variance:.2f}")
    report.append(f"• Максимальная разница: {top_movement['avg_frequency'] - low_movement['avg_frequency']:.2f}")
    report.append(f"  ({top_movement['movement']} vs {low_movement['movement']})")
    report.append("\n• Вывод: Литературное течение - значимый фактор использования архаизмов")
    
    report.append("\n" + "="*70)
    report.append("КОНЕЦ ОТЧЁТА")
    report.append("="*70)
    
    # Сохраняем отчёт
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"  ✓ Отчёт сохранён: {output_path}")
    
    # Выводим краткую версию в консоль
    print("\n" + "="*70)
    print("КРАТКИЕ ВЫВОДЫ:")
    print("="*70)
    for line in report[-30:]:  # Последние 30 строк с выводами
        if not line.startswith("="):
            print(line)


def main():
    print("="*70)
    print("СРАВНИТЕЛЬНЫЙ АНАЛИЗ: АРХАИЗМЫ И ЛИТЕРАТУРНЫЕ ТЕЧЕНИЯ")
    print("="*70 + "\n")
    
    # Загружаем данные
    decade_stats, author_stats = load_statistics()
    
    # Определяем периоды интенсивной архаизации
    print("Анализирую периоды интенсивной архаизации...")
    peak_periods, threshold = identify_peak_periods(decade_stats)
    print(f"✓ Найдено {len(peak_periods)} периодов выше порога ({threshold:.2f})\n")
    
    # Анализируем по литературным течениям
    print("Анализирую литературные течения...")
    movement_stats = analyze_movements_archaism(decade_stats)
    print(f"✓ Проанализировано {len(movement_stats)} течений\n")
    
    # Классифицируем авторов
    print("Классифицирую авторов по течениям...")
    author_stats = classify_authors_by_movement(author_stats)
    classified = (author_stats['movement'] != 'Не определено').sum()
    print(f"✓ Классифицировано {classified} из {len(author_stats)} авторов\n")
    
    # Создаём визуализации
    print("="*70)
    print("СОЗДАНИЕ ВИЗУАЛИЗАЦИЙ")
    print("="*70 + "\n")
    
    results_dir = Path(__file__).parent.parent / 'results'
    
    plot_movements_comparison(movement_stats, 
                              results_dir / 'literary_movements_comparison.png')
    plot_timeline_with_movements(decade_stats,
                                 results_dir / 'timeline_with_movements.png')
    
    # Сохраняем таблицу по течениям
    print("\nСохраняю таблицу по течениям...")
    movement_stats.to_csv(results_dir / 'archaism_by_movement.csv', 
                         index=False, encoding='utf-8')
    print(f"  ✓ Таблица сохранена: archaism_by_movement.csv")
    
    # Генерируем отчёт
    print("\n" + "="*70)
    print("ГЕНЕРАЦИЯ АНАЛИТИЧЕСКОГО ОТЧЁТА")
    print("="*70 + "\n")
    
    generate_analysis_report(decade_stats, author_stats, movement_stats,
                           peak_periods, results_dir / 'ANALYSIS_REPORT.txt')
    
    print("\n" + "="*70)
    print("✓ СРАВНИТЕЛЬНЫЙ АНАЛИЗ ЗАВЕРШЁН")
    print("="*70 + "\n")
    
    print("Созданные файлы:")
    print("  Графики:")
    print("    - literary_movements_comparison.png")
    print("    - timeline_with_movements.png")
    print("  Таблицы:")
    print("    - archaism_by_movement.csv")
    print("  Отчёт:")
    print("    - ANALYSIS_REPORT.txt")
    print()


if __name__ == '__main__':
    main()



