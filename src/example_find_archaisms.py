#!/usr/bin/env python3
"""
Пример поиска архаизмов в стихотворениях.
Демонстрирует использование словаря архаизмов для анализа текстов.
"""

import pandas as pd
import re
from pathlib import Path
from collections import Counter


def load_archaisms_set():
    """Загружает множество архаизмов из текстового файла."""
    project_root = Path(__file__).parent.parent
    wordlist_path = project_root / 'dataset' / 'archaisms_wordlist.txt'
    
    with open(wordlist_path, 'r', encoding='utf-8') as f:
        archaisms = set(line.strip().lower() for line in f if line.strip())
    
    print(f"✓ Загружено {len(archaisms)} архаизмов")
    return archaisms


def tokenize_text(text):
    """Простая токенизация текста (разбиение на слова)."""
    if not text:
        return []
    # Убираем знаки препинания и разбиваем на слова
    words = re.findall(r'\b[а-яёА-ЯЁ]+\b', text.lower())
    return words


def find_archaisms_in_text(text, archaisms_set):
    """
    Находит архаизмы в тексте.
    
    Returns:
        list: список найденных архаизмов
    """
    words = tokenize_text(text)
    found = [word for word in words if word in archaisms_set]
    return found


def analyze_poem(poem_row, archaisms_set):
    """Анализирует одно стихотворение на наличие архаизмов."""
    text = poem_row['text']
    words = tokenize_text(text)
    found_archaisms = find_archaisms_in_text(text, archaisms_set)
    
    total_words = len(words)
    archaism_count = len(found_archaisms)
    archaism_percentage = (archaism_count / total_words * 100) if total_words > 0 else 0
    
    return {
        'total_words': total_words,
        'archaism_count': archaism_count,
        'archaism_percentage': archaism_percentage,
        'found_archaisms': found_archaisms
    }


def main():
    # Загружаем данные
    project_root = Path(__file__).parent.parent
    poems_path = project_root / 'dataset' / 'poems.parquet'
    
    print("Загружаю стихотворения...")
    df = pd.read_parquet(poems_path)
    print(f"✓ Загружено {len(df)} стихотворений\n")
    
    # Загружаем словарь архаизмов
    print("Загружаю словарь архаизмов...")
    archaisms_set = load_archaisms_set()
    print()
    
    # Анализируем несколько примеров
    print("="*60)
    print("ПРИМЕРЫ АНАЛИЗА СТИХОТВОРЕНИЙ")
    print("="*60)
    
    # Пример 1: Лермонтов (XIX век)
    print("\n1. Михаил Лермонтов (1829):")
    lermontov = df[df['author'] == 'Михаил Лермонтов'].iloc[0]
    result = analyze_poem(lermontov, archaisms_set)
    print(f"   Название: {lermontov['name']}")
    print(f"   Всего слов: {result['total_words']}")
    print(f"   Архаизмов: {result['archaism_count']} ({result['archaism_percentage']:.1f}%)")
    if result['found_archaisms']:
        unique_archaisms = list(set(result['found_archaisms']))[:10]
        print(f"   Найденные архаизмы: {', '.join(unique_archaisms)}")
    
    # Пример 2: Есенин (XX век)
    print("\n2. Сергей Есенин (1917):")
    esenin = df[df['author'] == 'Сергей Есенин'].iloc[0]
    result = analyze_poem(esenin, archaisms_set)
    print(f"   Название: {esenin['name']}")
    print(f"   Всего слов: {result['total_words']}")
    print(f"   Архаизмов: {result['archaism_count']} ({result['archaism_percentage']:.1f}%)")
    if result['found_archaisms']:
        unique_archaisms = list(set(result['found_archaisms']))[:10]
        print(f"   Найденные архаизмы: {', '.join(unique_archaisms)}")
    
    # Пример 3: Пушкин (XIX век)
    print("\n3. Александр Пушкин:")
    pushkin = df[df['author'] == 'Александр Пушкин'].iloc[0]
    result = analyze_poem(pushkin, archaisms_set)
    print(f"   Название: {pushkin['name']}")
    print(f"   Год: {int(pushkin['year'])}")
    print(f"   Всего слов: {result['total_words']}")
    print(f"   Архаизмов: {result['archaism_count']} ({result['archaism_percentage']:.1f}%)")
    if result['found_archaisms']:
        unique_archaisms = list(set(result['found_archaisms']))[:10]
        print(f"   Найденные архаизмы: {', '.join(unique_archaisms)}")
    
    # Общая статистика по нескольким авторам
    print("\n" + "="*60)
    print("СРАВНЕНИЕ АВТОРОВ")
    print("="*60)
    
    authors_to_compare = ['Александр Пушкин', 'Михаил Лермонтов', 
                          'Сергей Есенин', 'Владимир Высоцкий']
    
    for author in authors_to_compare:
        author_poems = df[df['author'] == author]
        if len(author_poems) == 0:
            continue
        
        # Анализируем первые 10 стихотворений автора
        sample = author_poems.head(10)
        all_percentages = []
        
        for idx, poem in sample.iterrows():
            result = analyze_poem(poem, archaisms_set)
            all_percentages.append(result['archaism_percentage'])
        
        avg_percentage = sum(all_percentages) / len(all_percentages)
        print(f"\n{author}:")
        print(f"  Средний % архаизмов (в выборке из {len(sample)} стихов): {avg_percentage:.2f}%")
    
    print("\n" + "="*60)
    print("✓ Анализ завершен!")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()

