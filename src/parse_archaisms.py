#!/usr/bin/env python3
"""
Скрипт для парсинга словаря устаревших слов из файла устаревшие.txt
и конвертации в структурированный формат (CSV/Parquet).
"""

import pandas as pd
import re
from pathlib import Path


def parse_archaisms_file(file_path):
    """
    Парсит файл со словарем устаревших слов.
    
    Формат: "слово1, слово2 – определение"
    
    Returns:
        list of dict: список словарей с полями word, definition, variants
    """
    print(f"Начинаю парсинг {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    entries = []
    current_letter = None
    started_parsing = False  # Флаг начала парсинга словарных статей
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        
        # Пропускаем пустые строки
        if not line:
            continue
        
        # Проверяем, не является ли строка просто буквой (разделителем)
        if len(line) == 1 and line.isalpha() and line.isupper():
            current_letter = line
            started_parsing = True  # Начинаем парсить после первой буквы
            continue
        
        # Начинаем обрабатывать записи только после встречи первой буквы
        if not started_parsing:
            continue
        
        # Ищем паттерн "слово – определение"
        # Используем длинное тире (–) или обычное (-)
        match = re.match(r'^([^–\-]+?)\s*[–\-]\s*(.+)$', line)
        
        if match:
            words_part = match.group(1).strip()
            definition = match.group(2).strip()
            
            # Разбиваем слова по запятым
            words = [w.strip() for w in words_part.split(',')]
            
            # Основное слово - первое в списке
            main_word = words[0] if words else words_part
            
            # Убираем примечания в скобках из основного слова
            main_word_clean = re.sub(r'\s*\([^)]*\)', '', main_word).strip()
            
            # Варианты - остальные слова (если есть)
            variants = ', '.join(words[1:]) if len(words) > 1 else None
            
            entries.append({
                'word': main_word_clean,
                'definition': definition,
                'variants': variants,
                'letter': current_letter,
                'original': words_part
            })
    
    print(f"Парсинг завершен! Найдено записей: {len(entries)}")
    return entries


def analyze_dictionary(df):
    """Выводит статистику по словарю."""
    print("\n" + "="*60)
    print("СТАТИСТИКА СЛОВАРЯ УСТАРЕВШИХ СЛОВ")
    print("="*60)
    
    print(f"\nОбщее количество записей: {len(df)}")
    print(f"Записей с вариантами: {df['variants'].notna().sum()}")
    
    # Статистика по буквам
    print("\nРаспределение по буквам алфавита:")
    letter_counts = df['letter'].value_counts().sort_index()
    for letter, count in letter_counts.items():
        if letter:
            print(f"  {letter}: {count}")
    
    # Примеры записей
    print("\nПримеры записей:")
    for i, row in df.head(5).iterrows():
        variants_str = f" (варианты: {row['variants']})" if row['variants'] else ""
        print(f"  {row['word']}{variants_str} – {row['definition'][:60]}...")
    
    # Слова с вариантами
    print("\nПримеры слов с вариантами написания:")
    with_variants = df[df['variants'].notna()].head(5)
    for i, row in with_variants.iterrows():
        print(f"  {row['word']} (варианты: {row['variants']})")
    
    print("="*60 + "\n")


def extract_simple_word_list(df):
    """
    Извлекает простой список всех слов (основных + варианты).
    Для использования в анализе текстов.
    """
    all_words = set()
    
    # Добавляем основные слова
    all_words.update(df['word'].str.lower())
    
    # Добавляем варианты
    for variants in df['variants'].dropna():
        for variant in variants.split(','):
            variant = variant.strip()
            if variant:
                # Убираем примечания в скобках
                variant_clean = re.sub(r'\s*\([^)]*\)', '', variant).strip()
                all_words.add(variant_clean.lower())
    
    return sorted(all_words)


def main():
    # Пути к файлам
    project_root = Path(__file__).parent.parent
    input_path = project_root / 'dataset' / 'устаревшие.txt'
    csv_path = project_root / 'dataset' / 'archaisms.csv'
    parquet_path = project_root / 'dataset' / 'archaisms.parquet'
    wordlist_path = project_root / 'dataset' / 'archaisms_wordlist.txt'
    
    # Проверяем наличие входного файла
    if not input_path.exists():
        print(f"ОШИБКА: Файл {input_path} не найден!")
        return 1
    
    # Парсим файл
    entries = parse_archaisms_file(input_path)
    
    # Создаем DataFrame
    df = pd.DataFrame(entries)
    
    # Выводим статистику
    analyze_dictionary(df)
    
    # Сохраняем в CSV
    print(f"Сохраняю в CSV: {csv_path}")
    df.to_csv(csv_path, index=False, encoding='utf-8')
    csv_size_kb = csv_path.stat().st_size / 1024
    print(f"  ✓ CSV сохранен ({csv_size_kb:.2f} KB)")
    
    # Сохраняем в Parquet
    print(f"\nСохраняю в Parquet: {parquet_path}")
    df.to_parquet(parquet_path, index=False)
    parquet_size_kb = parquet_path.stat().st_size / 1024
    print(f"  ✓ Parquet сохранен ({parquet_size_kb:.2f} KB)")
    
    # Создаем простой список слов для быстрого поиска
    print(f"\nСоздаю список слов: {wordlist_path}")
    word_list = extract_simple_word_list(df)
    with open(wordlist_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(word_list))
    print(f"  ✓ Список из {len(word_list)} уникальных слов сохранен")
    
    print(f"\n✓ Обработка завершена успешно!")
    print(f"  Записей в словаре: {len(df)}")
    print(f"  Уникальных слов (с вариантами): {len(word_list)}")
    print(f"  Размер CSV: {csv_size_kb:.2f} KB")
    print(f"  Размер Parquet: {parquet_size_kb:.2f} KB")


if __name__ == '__main__':
    main()

