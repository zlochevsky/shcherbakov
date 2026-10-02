#!/usr/bin/env python3
"""Привести HTML заметки «Словаря» (comments.body) к правилам разметки.

    python3 normalize.py заметка.html            # результат — в stdout, замечания — в stderr
    python3 normalize.py --source старая.html    # текст со старого сайта: <em> → <i>, <b> → <em> (не повторять!)
    python3 normalize.py < заметка.html

Правила — в docstring slovar_markup.py и в docs/directus.md (коллекция comments).
Скрипт ничего не пишет в базу: результат вставляется в поле body в Directus вручную.
Курсив (слова автора / чужие цитаты) скрипт не расставляет — это решает человек.
"""
import argparse, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from slovar_markup import normalize_body

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('file', nargs='?', help='HTML-файл (по умолчанию stdin)')
ap.add_argument('--source', action='store_true', help='текст из исходника старого сайта (замена <em>/<b>, не идемпотентно)')
args = ap.parse_args()

body = open(args.file, encoding='utf-8').read() if args.file else sys.stdin.read()
report = []
sys.stdout.write(normalize_body(body, report, source=args.source))
for line in report:
    print('!', line, file=sys.stderr)
