#!/usr/bin/env python3
"""
Анализ частотности слов по векам с визуализацией в виде облаков слов.
Создаёт облака для наиболее частых и наиболее редких слов по 18, 19 и 20 векам.
"""

import pandas as pd
import re
from pathlib import Path
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt


def load_poems():
    """Загружает датасет стихотворений."""
    project_root = Path(__file__).parent.parent
    poems_path = project_root / 'dataset' / 'poems.parquet'
    
    print(f"Загружаю стихотворения из {poems_path}...")
    df = pd.read_parquet(poems_path)
    print(f"✓ Загружено {len(df)} стихотворений\n")
    return df


def tokenize_text(text):
    """Токенизация текста - извлечение русских слов."""
    if not text or not isinstance(text, str):
        return []
    # Извлекаем только русские слова длиной >= 3 символов
    words = re.findall(r'\b[а-яёА-ЯЁ]{3,}\b', text.lower())
    return words


def get_century(year):
    """Определяет век по году."""
    if pd.isna(year):
        return None
    year = int(year)
    return (year - 1) // 100 + 1


def collect_words_by_century(df, century):
    """Собирает все слова из стихотворений указанного века."""
    print(f"Обрабатываю {century} век...")
    
    # Добавляем колонку с веком
    df_temp = df.copy()
    df_temp['century'] = df_temp['year'].apply(get_century)
    
    # Фильтруем по веку
    century_poems = df_temp[df_temp['century'] == century]
    
    print(f"  Найдено стихотворений: {len(century_poems)}")
    
    # Собираем все слова
    all_words = []
    for text in century_poems['text']:
        words = tokenize_text(text)
        all_words.extend(words)
    
    print(f"  Всего слов: {len(all_words)}")
    print(f"  Уникальных слов: {len(set(all_words))}")
    
    return all_words


def create_word_cloud(word_freq, title, output_path, invert=False, max_words=200):
    """
    Создаёт облако слов.
    
    Args:
        word_freq: словарь {слово: частота}
        title: заголовок
        output_path: путь для сохранения
        invert: если True, то редкие слова будут крупнее
        max_words: максимальное количество слов в облаке
    """
    if invert:
        # Инвертируем частоты: редкие слова становятся "частыми"
        max_freq = max(word_freq.values())
        word_freq_inv = {word: max_freq - freq + 1 for word, freq in word_freq.items()}
        word_freq = word_freq_inv
    
    # Создаём облако слов
    wordcloud = WordCloud(
        width=1600,
        height=900,
        background_color='white',
        max_words=max_words,
        relative_scaling=0.5,
        min_font_size=10,
        font_path=None,  # Используем системный шрифт
        collocations=False,
        colormap='viridis'
    ).generate_from_frequencies(word_freq)
    
    # Создаём фигуру
    plt.figure(figsize=(16, 9))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(title, fontsize=20, pad=20)
    plt.tight_layout(pad=0)
    
    # Сохраняем
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Сохранено: {output_path}")


def filter_stopwords(word_freq, min_freq=5):
    """
    Фильтрует слишком редкие слова и возможные стоп-слова.
    
    Args:
        word_freq: Counter объект с частотами
        min_freq: минимальная частота для включения слова
    """
    # Базовые стоп-слова (союзы, предлоги, частицы)
    stopwords = {
        'что', 'как', 'это', 'все', 'его', 'еще', 'уже', 'для', 'так',
        'где', 'кто', 'меня', 'она', 'они', 'мне', 'тот', 'том', 'без',
        'под', 'над', 'при', 'про', 'или', 'тут', 'там', 'вот', 'весь',
        'эти', 'если', 'ему', 'ней', 'них', 'мой', 'мои', 'твой', 'свой',
        'того', 'чем', 'которые', 'которых', 'была', 'было', 'были', 'будет'
    }
    
    # Фильтруем
    filtered = {
        word: freq for word, freq in word_freq.items()
        if freq >= min_freq and word not in stopwords
    }
    
    return filtered


def main():
    # Создаём папку для результатов
    project_root = Path(__file__).parent.parent
    results_dir = project_root / 'results'
    results_dir.mkdir(exist_ok=True)
    
    print("="*60)
    print("АНАЛИЗ ЧАСТОТНОСТИ СЛОВ ПО ВЕКАМ")
    print("="*60 + "\n")
    
    # Загружаем данные
    df = load_poems()
    
    # Анализируем по векам
    centuries = [18, 19, 20]
    
    for century in centuries:
        print(f"\n{'='*60}")
        print(f"ВЕК: {century}")
        print(f"{'='*60}\n")
        
        # Собираем слова
        words = collect_words_by_century(df, century)
        
        if not words:
            print(f"⚠ Нет данных для {century} века, пропускаем...\n")
            continue
        
        # Считаем частоты
        word_freq = Counter(words)
        print(f"  Топ-10 слов: {word_freq.most_common(10)}")
        
        # Фильтруем стоп-слова и редкие слова
        word_freq_filtered = filter_stopwords(word_freq, min_freq=3)
        print(f"  После фильтрации осталось: {len(word_freq_filtered)} слов\n")
        
        # === ОБЛАКО ЧАСТЫХ СЛОВ (обычное) ===
        print("  Создаю облако частых слов...")
        output_normal = results_dir / f'wordcloud_{century}_century_frequent.png'
        create_word_cloud(
            word_freq_filtered,
            f'Наиболее частые слова в поэзии {century} века',
            output_normal,
            invert=False
        )
        
        # === ОБЛАКО РЕДКИХ СЛОВ (инвертированное) ===
        print("  Создаю облако редких слов...")
        output_inverted = results_dir / f'wordcloud_{century}_century_rare.png'
        create_word_cloud(
            word_freq_filtered,
            f'Наиболее редкие слова в поэзии {century} века',
            output_inverted,
            invert=True
        )
        
        print()
    
    print("="*60)
    print("✓ Все визуализации созданы!")
    print(f"Результаты сохранены в: {results_dir}")
    print("="*60 + "\n")
    
    # Выводим список созданных файлов
    print("Созданные файлы:")
    for img_file in sorted(results_dir.glob('wordcloud_*.png')):
        size_mb = img_file.stat().st_size / (1024 * 1024)
        print(f"  - {img_file.name} ({size_mb:.2f} MB)")


if __name__ == '__main__':
    main()

