# Отчёт по курсовой работе

## Описание

Данная папка содержит LaTeX-файл курсовой работы по корпусному анализу архаизации русской поэтической лексики.

## Структура файлов

- `report.tex` - исходный LaTeX-файл отчёта
- `report.pdf` - скомпилированный PDF-документ
- `требования.txt` - требования к оформлению работы

## Компиляция LaTeX в PDF

### Требования

Для компиляции документа необходим XeLaTeX компилятор с поддержкой русского языка и шрифта Times New Roman.

**macOS:**
```bash
# Установка TeX Live (включает XeLaTeX)
brew install --cask mactex
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install texlive-full texlive-xetex texlive-lang-cyrillic
```

**Windows:**
- Скачайте и установите [MiKTeX](https://miktex.org/) или [TeX Live](https://www.tug.org/texlive/)

### Компиляция

Для компиляции документа выполните следующую команду из папки `report/`:

```bash
xelatex report.tex
```

Для корректной генерации оглавления и гиперссылок рекомендуется запустить компиляцию дважды:

```bash
xelatex report.tex
xelatex report.tex
```

Или используйте однострочную команду:

```bash
xelatex -interaction=nonstopmode report.tex && xelatex -interaction=nonstopmode report.tex
```

### Очистка временных файлов

После компиляции создаются временные файлы (`.aux`, `.log`, `.out` и др.), которые можно удалить:

```bash
rm -f *.aux *.log *.out *.toc
```

## Особенности документа

- Шрифт: Times New Roman 14pt
- Поля: левое 3 см, остальные 2 см
- Межстрочный интервал: 1.0
- Абзацный отступ: 1.25 см
- Графики включены из папки `../results/`
- Используется библиотека `fontspec` для работы со шрифтами

## Графики и иллюстрации

Документ содержит следующие графики из папки `results/`:
- `archaism_dynamics_by_decade.png` - динамика по десятилетиям
- `literary_movements_comparison.png` - сравнение течений
- `timeline_with_movements.png` - временная шкала
- `archaism_by_century.png` - сравнение по векам

Убедитесь, что эти файлы существуют перед компиляцией.

## Проблемы и решения

**Ошибка: "Font 'Times New Roman' not found"**
- macOS: Шрифт должен быть установлен по умолчанию
- Linux: Установите пакет `ttf-mscorefonts-installer`
- Windows: Шрифт входит в состав системы

**Ошибка: "File not found: ../results/..."**
- Убедитесь, что вы находитесь в папке `report/` при компиляции
- Проверьте наличие всех графиков в папке `results/`

**Предупреждения "Overfull \hbox"**
- Это предупреждения о выходе текста за границы строки
- Не критичны для данной работы, но можно исправить перефразированием

