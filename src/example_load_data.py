#!/usr/bin/env python3
"""
Пример загрузки и базовой работы с датасетом стихотворений.
"""

import pandas as pd
from pathlib import Path

def load_poems_csv():
    """Загружает датасет из CSV файла."""
    project_root = Path(__file__).parent.parent
    csv_path = project_root / 'dataset' / 'poems.csv'
    print(f"Загружаю CSV из {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"✓ Загружено {len(df)} стихотворений")
    return df

def load_poems_parquet():
    """Загружает датасет из Parquet файла (быстрее!)."""
    project_root = Path(__file__).parent.parent
    parquet_path = project_root / 'dataset' / 'poems.parquet'
    print(f"Загружаю Parquet из {parquet_path}...")
    df = pd.read_parquet(parquet_path)
    print(f"✓ Загружено {len(df)} стихотворений")
    return df

def main():
    # Загружаем данные (Parquet быстрее)
    df = load_poems_parquet()
    
    print("\n" + "="*60)
    print("СТРУКТУРА ДАННЫХ")
    print("="*60)
    print(f"\nКолонки: {list(df.columns)}")
    print(f"\nПервые 3 записи:")
    print(df[['author', 'name', 'year']].head(3))
    
    print("\n" + "="*60)
    print("ПРИМЕРЫ АНАЛИЗА")
    print("="*60)
    
    # Фильтрация по автору
    print("\n1. Стихотворения Пушкина:")
    pushkin = df[df['author'] == 'Александр Пушкин']
    print(f"   Всего стихотворений: {len(pushkin)}")
    print(f"   Период: {int(pushkin['year'].min())} - {int(pushkin['year'].max())}")
    
    # Фильтрация по периоду
    print("\n2. Стихотворения 1920-х годов:")
    twenties = df[(df['year'] >= 1920) & (df['year'] < 1930)]
    print(f"   Всего стихотворений: {len(twenties)}")
    print(f"   Топ-3 автора:")
    for i, (author, count) in enumerate(twenties['author'].value_counts().head(3).items(), 1):
        print(f"     {i}. {author}: {count}")
    
    # Стихотворения с темами
    print("\n3. Стихотворения с темами:")
    with_themes = df[df['themes'].notna()]
    print(f"   Всего: {len(with_themes)}")
    print(f"   Пример тем: {with_themes['themes'].head(3).tolist()}")
    
    # Средняя длина текста по авторам
    print("\n4. Средняя длина текста (в символах) у топ-5 авторов:")
    df['text_length'] = df['text'].str.len()
    top_authors = df['author'].value_counts().head(5).index
    for author in top_authors:
        author_df = df[df['author'] == author]
        avg_length = author_df['text_length'].mean()
        print(f"   {author}: {avg_length:.0f} символов")
    
    print("\n" + "="*60)
    print("✓ Данные готовы к анализу!")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()

