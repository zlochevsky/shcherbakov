#!/usr/bin/env python3
"""
Автоматическое обновление textFinishAtLine во всех .md файлах
на основе позиции года в соответствующих .txt файлах
"""

import json
import re
import os
from pathlib import Path

def find_year_line(txt_path):
    """Найти номер строки с годом (4 цифры отдельно в строке)"""
    if not txt_path.exists():
        return None

    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Паттерн: 4 цифры, возможно с ведущими пробелами, отдельно в строке
    year_pattern = re.compile(r'^\s*(\d{4})\s*$')

    for i, line in enumerate(lines):
        # Пропускаем первые 5 строк (название может содержать год)
        if i < 5:
            continue

        match = year_pattern.match(line)
        if match:
            # Возвращаем номер строки + 1 (Hugo использует 1-based индексацию)
            # И ещё +1, потому что нам нужна строка ПОСЛЕ года
            return i + 2

    return None

def update_md_file(md_path):
    """Обновить textFinishAtLine в .md файле"""
    with open(md_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Получаем id песни
    song_id = data.get('params', {}).get('id')
    if not song_id:
        print(f"⚠ {md_path}: нет id")
        return False

    # Находим соответствующий .txt файл
    txt_path = Path('assets/texts') / f"{song_id}.txt"

    # Ищем год в .txt файле
    year_line = find_year_line(txt_path)

    if year_line is None:
        print(f"⚠ {md_path.name}: год не найден в {txt_path.name}")
        return False

    # Получаем текущее значение
    old_value = data.get('params', {}).get('textFinishAtLine')

    # Обновляем значение
    if 'params' not in data:
        data['params'] = {}
    data['params']['textFinishAtLine'] = year_line

    # Записываем обратно
    with open(md_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    if old_value != year_line:
        print(f"✓ {md_path.name}: {old_value} → {year_line}")
        return True
    else:
        print(f"  {md_path.name}: уже {year_line}")
        return False

def main():
    """Главная функция"""
    base_path = Path('content/texts')

    if not base_path.exists():
        print(f"❌ Директория {base_path} не найдена")
        return

    # Находим все .md файлы
    md_files = sorted(base_path.rglob('*.md'))

    print(f"Найдено {len(md_files)} файлов")
    print("=" * 60)

    updated = 0
    not_found = 0
    unchanged = 0

    for md_path in md_files:
        result = update_md_file(md_path)
        if result is True:
            updated += 1
        elif result is False:
            not_found += 1
        else:
            unchanged += 1

    print("=" * 60)
    print(f"✓ Обновлено: {updated}")
    print(f"  Без изменений: {unchanged}")
    print(f"⚠ Год не найден: {not_found}")

if __name__ == '__main__':
    main()