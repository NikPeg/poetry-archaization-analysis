#!/usr/bin/env python3
"""
Скрипт для добавления архаизмов из ручного списка (устаревшие_из_облака.txt)
в основной словарь архаизмов.
"""

import pandas as pd
from pathlib import Path


def load_manual_archaisms(file_path):
    """
    Загружает список архаизмов из текстового файла.
    Убирает пустые строки и пробелы.
    """
    print(f"Загружаю ручной список из {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Очищаем от пробелов и пустых строк
    words = []
    for line in lines:
        word = line.strip()
        if word:  # Пропускаем пустые строки
            words.append(word.lower())
    
    # Убираем дубликаты
    unique_words = sorted(set(words))
    
    print(f"✓ Загружено {len(words)} слов ({len(unique_words)} уникальных)")
    return unique_words


def load_existing_archaisms(csv_path):
    """Загружает существующий словарь архаизмов."""
    print(f"\nЗагружаю существующий словарь из {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"✓ Загружено {len(df)} записей")
    
    # Получаем множество всех существующих слов (основных + варианты)
    existing_words = set()
    
    # Основные слова
    existing_words.update(df['word'].str.lower())
    
    # Варианты (если есть)
    for variants in df['variants'].dropna():
        for variant in variants.split(','):
            word = variant.strip().lower()
            if word:
                existing_words.add(word)
    
    print(f"  Уникальных слов (с вариантами): {len(existing_words)}")
    return df, existing_words


def add_new_archaisms(df_existing, existing_words, new_words):
    """
    Добавляет новые архаизмы в DataFrame.
    
    Returns:
        tuple: (обновлённый DataFrame, количество добавленных слов)
    """
    print("\n" + "="*60)
    print("АНАЛИЗ НОВЫХ СЛОВ")
    print("="*60)
    
    words_to_add = []
    already_exist = []
    
    for word in new_words:
        if word in existing_words:
            already_exist.append(word)
        else:
            words_to_add.append(word)
    
    print(f"\nВсего слов для проверки: {len(new_words)}")
    print(f"  ✓ Уже есть в словаре: {len(already_exist)}")
    print(f"  + Новых слов для добавления: {len(words_to_add)}")
    
    if already_exist:
        print(f"\n  Слова, которые уже есть:")
        for word in already_exist[:10]:  # Показываем первые 10
            print(f"    - {word}")
        if len(already_exist) > 10:
            print(f"    ... и ещё {len(already_exist) - 10} слов")
    
    if words_to_add:
        print(f"\n  Новые слова для добавления:")
        for word in words_to_add:
            print(f"    + {word}")
    
    # Создаём новые записи для добавления
    new_rows = []
    for word in words_to_add:
        new_rows.append({
            'word': word.capitalize(),  # Приводим к стандартному виду
            'definition': 'Добавлено из анализа облаков слов (ручная проверка)',
            'variants': None,
            'letter': word[0].upper(),
            'original': word.capitalize()
        })
    
    if new_rows:
        # Добавляем новые строки в DataFrame
        df_new = pd.DataFrame(new_rows)
        df_updated = pd.concat([df_existing, df_new], ignore_index=True)
        
        # Сортируем по слову
        df_updated = df_updated.sort_values('word').reset_index(drop=True)
    else:
        df_updated = df_existing
    
    return df_updated, len(words_to_add)


def update_wordlist(wordlist_path, df):
    """
    Обновляет текстовый файл со списком слов.
    """
    print(f"\nОбновляю список слов: {wordlist_path}...")
    
    all_words = set()
    
    # Добавляем основные слова
    all_words.update(df['word'].str.lower())
    
    # Добавляем варианты
    for variants in df['variants'].dropna():
        for variant in variants.split(','):
            word = variant.strip().lower()
            if word:
                all_words.add(word)
    
    # Сохраняем отсортированный список
    with open(wordlist_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sorted(all_words)))
    
    print(f"✓ Обновлено: {len(all_words)} уникальных слов")


def main():
    # Пути к файлам
    project_root = Path(__file__).parent.parent
    manual_file = project_root / 'dataset' / 'устаревшие_из_облака.txt'
    csv_path = project_root / 'dataset' / 'archaisms.csv'
    parquet_path = project_root / 'dataset' / 'archaisms.parquet'
    wordlist_path = project_root / 'dataset' / 'archaisms_wordlist.txt'
    
    print("="*60)
    print("ДОБАВЛЕНИЕ АРХАИЗМОВ ИЗ РУЧНОГО СПИСКА")
    print("="*60 + "\n")
    
    # Проверяем наличие файла
    if not manual_file.exists():
        print(f"ОШИБКА: Файл {manual_file} не найден!")
        return 1
    
    # Загружаем данные
    new_words = load_manual_archaisms(manual_file)
    df_existing, existing_words = load_existing_archaisms(csv_path)
    
    # Добавляем новые слова
    df_updated, added_count = add_new_archaisms(df_existing, existing_words, new_words)
    
    # Сохраняем обновлённые данные
    if added_count > 0:
        print("\n" + "="*60)
        print("СОХРАНЕНИЕ ОБНОВЛЁННОГО СЛОВАРЯ")
        print("="*60)
        
        # Сохраняем CSV
        print(f"\nСохраняю CSV: {csv_path}")
        df_updated.to_csv(csv_path, index=False, encoding='utf-8')
        csv_size_kb = csv_path.stat().st_size / 1024
        print(f"  ✓ CSV сохранён ({csv_size_kb:.2f} KB)")
        
        # Сохраняем Parquet
        print(f"\nСохраняю Parquet: {parquet_path}")
        df_updated.to_parquet(parquet_path, index=False)
        parquet_size_kb = parquet_path.stat().st_size / 1024
        print(f"  ✓ Parquet сохранён ({parquet_size_kb:.2f} KB)")
        
        # Обновляем список слов
        update_wordlist(wordlist_path, df_updated)
    else:
        print("\n" + "="*60)
        print("⚠ Новых слов для добавления нет")
        print("="*60)
    
    # Итоговая статистика
    print("\n" + "="*60)
    print("ИТОГОВАЯ СТАТИСТИКА")
    print("="*60)
    print(f"\nБыло записей в словаре: {len(df_existing)}")
    print(f"Стало записей в словаре: {len(df_updated)}")
    print(f"\n📊 Результат проверки {len(new_words)} слов:")
    print(f"  ✓ Уже присутствовали: {len(new_words) - added_count}")
    print(f"  + Добавлено новых: {added_count}")
    
    if added_count > 0:
        print(f"\n✓ Словарь успешно обновлён!")
    else:
        print(f"\n✓ Словарь не изменён (все слова уже были)")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()

