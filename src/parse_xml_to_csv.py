#!/usr/bin/env python3
"""
Скрипт для парсинга XML датасета стихотворений и конвертации в CSV/Parquet формат.
"""

import xml.etree.ElementTree as ET
import pandas as pd
from pathlib import Path
import sys

def parse_xml_to_dataframe(xml_path):
    """
    Парсит XML файл со стихотворениями и возвращает pandas DataFrame.
    
    Args:
        xml_path: путь к XML файлу
        
    Returns:
        pandas.DataFrame с колонками: author, name, text, date_from, date_to, themes, year
    """
    print(f"Начинаю парсинг {xml_path}...")
    
    # Парсим XML
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    # Список для хранения данных
    poems_data = []
    
    # Итерируемся по всем стихотворениям
    for idx, item in enumerate(root.findall('item'), 1):
        # Извлекаем данные
        author = item.find('author')
        name = item.find('name')
        text = item.find('text')
        date_from = item.find('date_from')
        date_to = item.find('date_to')
        themes = item.find('themes')
        
        # Получаем текстовые значения (или None если тег пустой)
        author_text = author.text if author is not None else None
        name_text = name.text if name is not None else None
        text_text = text.text if text is not None else None
        date_from_text = date_from.text if date_from is not None and date_from.text else None
        date_to_text = date_to.text if date_to is not None and date_to.text else None
        
        # Обработка тем
        themes_list = []
        if themes is not None:
            for theme_item in themes.findall('item'):
                if theme_item.text:
                    themes_list.append(theme_item.text)
        themes_text = ', '.join(themes_list) if themes_list else None
        
        # Вычисляем средний год написания
        year = None
        try:
            if date_from_text and date_to_text:
                year = (int(date_from_text) + int(date_to_text)) // 2
            elif date_from_text:
                year = int(date_from_text)
            elif date_to_text:
                year = int(date_to_text)
        except (ValueError, TypeError):
            pass
        
        poems_data.append({
            'author': author_text,
            'name': name_text,
            'text': text_text,
            'date_from': date_from_text,
            'date_to': date_to_text,
            'themes': themes_text,
            'year': year
        })
        
        # Прогресс каждые 1000 стихотворений
        if idx % 1000 == 0:
            print(f"  Обработано {idx} стихотворений...")
    
    print(f"Парсинг завершен! Всего стихотворений: {len(poems_data)}")
    
    # Создаем DataFrame
    df = pd.DataFrame(poems_data)
    return df


def analyze_dataset(df):
    """Выводит базовую статистику по датасету."""
    print("\n" + "="*60)
    print("СТАТИСТИКА ДАТАСЕТА")
    print("="*60)
    
    print(f"\nОбщее количество стихотворений: {len(df)}")
    print(f"Количество уникальных авторов: {df['author'].nunique()}")
    
    # Статистика по датам
    poems_with_dates = df[df['year'].notna()]
    print(f"\nСтихотворений с датами: {len(poems_with_dates)} ({len(poems_with_dates)/len(df)*100:.1f}%)")
    if len(poems_with_dates) > 0:
        print(f"Диапазон годов: {int(poems_with_dates['year'].min())} - {int(poems_with_dates['year'].max())}")
    
    # Статистика по темам
    poems_with_themes = df[df['themes'].notna()]
    print(f"\nСтихотворений с темами: {len(poems_with_themes)} ({len(poems_with_themes)/len(df)*100:.1f}%)")
    
    # Топ-10 авторов
    print("\nТоп-10 авторов по количеству стихотворений:")
    top_authors = df['author'].value_counts().head(10)
    for i, (author, count) in enumerate(top_authors.items(), 1):
        print(f"  {i:2d}. {author}: {count}")
    
    # Распределение по десятилетиям
    if len(poems_with_dates) > 0:
        print("\nРаспределение по десятилетиям:")
        df_with_year = df[df['year'].notna()].copy()
        df_with_year['decade'] = (df_with_year['year'] // 10) * 10
        decade_counts = df_with_year['decade'].value_counts().sort_index()
        for decade, count in decade_counts.items():
            print(f"  {int(decade)}s: {count}")
    
    print("="*60 + "\n")


def main():
    # Пути к файлам
    project_root = Path(__file__).parent.parent
    xml_path = project_root / 'dataset' / 'all.xml'
    csv_path = project_root / 'dataset' / 'poems.csv'
    parquet_path = project_root / 'dataset' / 'poems.parquet'
    
    # Проверяем наличие XML файла
    if not xml_path.exists():
        print(f"ОШИБКА: Файл {xml_path} не найден!")
        sys.exit(1)
    
    # Парсим XML
    df = parse_xml_to_dataframe(xml_path)
    
    # Выводим статистику
    analyze_dataset(df)
    
    # Сохраняем в CSV
    print(f"Сохраняю в CSV: {csv_path}")
    df.to_csv(csv_path, index=False, encoding='utf-8')
    csv_size_mb = csv_path.stat().st_size / (1024 * 1024)
    print(f"  ✓ CSV сохранен ({csv_size_mb:.2f} MB)")
    
    # Сохраняем в Parquet
    print(f"\nСохраняю в Parquet: {parquet_path}")
    df.to_parquet(parquet_path, index=False)
    parquet_size_mb = parquet_path.stat().st_size / (1024 * 1024)
    print(f"  ✓ Parquet сохранен ({parquet_size_mb:.2f} MB)")
    
    print(f"\n✓ Обработка завершена успешно!")
    print(f"  Размер CSV: {csv_size_mb:.2f} MB")
    print(f"  Размер Parquet: {parquet_size_mb:.2f} MB")
    print(f"  Экономия: {(1 - parquet_size_mb/csv_size_mb)*100:.1f}%")


if __name__ == '__main__':
    main()

