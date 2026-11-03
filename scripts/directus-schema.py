#!/usr/bin/env python3
"""Снимок схемы Directus и схемы связей коллекций в docs/directus.md.

Запускать после каждого изменения модели данных в Directus:

    DIRECTUS_ADMIN_TOKEN=… python3 scripts/directus-schema.py --fetch

--fetch  забрать свежий снимок (GET /schema/snapshot, нужен токен администратора
         в переменной окружения DIRECTUS_ADMIN_TOKEN) в docs/directus-snapshot.json;
без него  взять уже лежащий там снимок.

Дальше скрипт всегда:
  1) заменяет точную версию Directus в снимке на мажорную («11»): репозиторий
     публичный, а сам Directus версию анонимам не показывает;
  2) пересобирает схемы Mermaid в docs/directus.md между метками
     <!-- schema:begin --> и <!-- schema:end -->.

Какая коллекция на какой схеме — решает человек: список GROUPS ниже.
Коллекция, которой нет ни в одной группе, попадает на схему «Не распределены»,
и скрипт об этом пишет. Служебные таблицы «многие ко многим» (скрытые в Directus)
отдельно не рисуются: связь через них — одна линия }o--o{ между двумя коллекциями.
"""
import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT = ROOT / 'docs' / 'directus-snapshot.json'
DOC = ROOT / 'docs' / 'directus.md'
BEGIN, END = '<!-- schema:begin -->', '<!-- schema:end -->'
API = 'https://db.sch.com.ru/schema/snapshot'

# Порядок групп = порядок схем в документе. Линия рисуется, только если ОБЕ коллекции
# в группе, поэтому общие (works, performers, links…) вписаны в каждую тему, где нужны.
# Элемент группы — имя коллекции (пустой блок) или (имя, [поля]) — блок с этими полями
# в этом порядке; '*' вместо списка — все поля. У одной коллекции в разных группах
# поля могут быть разными.
GROUPS = [
    ('Издания', [('works', ['id']), 
                ('books', ['id', 'series', 'name', 'fullname', 'show_on_catalogpage', 'show_on_songpage']), 
                'book_sets', 
                ('books_entries',['works_id', 'books_id', 'page']), 
                ]),
    ('Комментарии', ['works', 'comments', 'works_see_also']),
    ('Песни', [('works', ['name', 'sort', 'incipit', 'fincipit', 'hidden', 'date', 'edit', 'author', 'music'])]),
    ('Варианты', ['works', 'variants', 'perfs', 'books_entries']),
    ('Исполнения', ['works', 'events', 'perfs']),
    ('События', ['events', 'announces']),
    ('Диски', [('works', ['id']), ('perfs', ['events_id', 'works_id', 'num']), ('sets',['title', 'year', 'ignore_in_catalogue']), ('sets_entries', ['perfs_id', 'sets_id', 'num']), 'disk_formats']),
    ('Исполнители', ['works', 'releases', 'recordings', 'performers', 'links']),
    ('Переводы', ['works', 'translations', 'languages', 'translators']),
    ('Циклы', ['works', 'cycles', 'cycles_entries']),
    ('Лог', ['events', 'log_entries']),
    ('Высказывания', ['works', 'statements']),
]


def fetch():
    tok = os.environ.get('DIRECTUS_ADMIN_TOKEN')
    if not tok:
        sys.exit('нет токена: задайте DIRECTUS_ADMIN_TOKEN (снимок схемы отдаётся только администратору)')
    req = urllib.request.Request(API, headers={'Authorization': 'Bearer ' + tok})
    return json.load(urllib.request.urlopen(req))


def edges(snap):
    """Связи между пользовательскими коллекциями: (many, one, подпись, вид)."""
    data = snap['data']
    hidden = {c['collection'] for c in data['collections'] if (c.get('meta') or {}).get('hidden')}
    nullable = {(f['collection'], f['field']): (f.get('schema') or {}).get('is_nullable', True)
                for f in data['fields']}
    rels = [r for r in data['relations']
            if not r['collection'].startswith('directus_') and r['related_collection']
            and not r['related_collection'].startswith('directus_')]
    out = []
    m2m = {}  # служебная таблица → (коллекция, поле M2M) с каждой стороны, где поле заведено
    for r in rels:
        m = r.get('meta') or {}
        if r['collection'] in hidden:
            if m.get('one_field'):
                m2m.setdefault(r['collection'], []).append((r['related_collection'], m['one_field'],
                                                            m.get('junction_field')))
            continue
        kind = 'm2o?' if nullable.get((r['collection'], r['field']), True) else 'm2o'
        out.append((r['collection'], r['related_collection'], r['field'], kind))
    # одна линия на служебную таблицу, даже если поле M2M заведено с обеих сторон
    for junction, sides in m2m.items():
        a, field, jf = sorted(sides)[0]
        other = next(x['related_collection'] for x in rels if x['collection'] == junction and x['field'] == jf)
        label = ' / '.join(f for _, f, _ in sorted(sides))
        out.append((a, other, label, 'm2m'))
    return sorted(set(out)), hidden


def mermaid(lines):
    return '```mermaid\nerDiagram\n' + ''.join('    ' + s + '\n' for s in lines) + '```\n'


def block(snap, coll, wanted):
    """Блок коллекции с полями: «тип имя PK/FK» в синтаксисе erDiagram."""
    fields = {f['field']: f for f in snap['data']['fields'] if f['collection'] == coll}
    fks = {r['field'] for r in snap['data']['relations'] if r['collection'] == coll}
    names = list(fields) if wanted == '*' else wanted
    rows = []
    for n in names:
        f = fields.get(n)
        if not f:
            print(f'Нет поля {coll}.{n} (GROUPS)', file=sys.stderr)
            continue
        key = ' PK' if (f.get('schema') or {}).get('is_primary_key') else ' FK' if n in fks else ''
        rows.append(f'    {f["type"]} {n}{key}')
    return [coll + ' {'] + rows + ['}']


def render(snap):
    es, hidden = edges(snap)
    shown = {c['collection'] for c in snap['data']['collections']} - hidden
    norm = [(t, [(c, None) if isinstance(c, str) else (c[0], c[1]) for c in cs]) for t, cs in GROUPS]
    grouped = {c for _, cs in norm for c, _ in cs}
    groups = list(norm)
    rest = sorted(shown - grouped)
    if rest:
        print('Не распределены по схемам (добавьте в GROUPS):', ', '.join(rest), file=sys.stderr)
        groups.append(('Не распределены', [(c, None) for c in rest]))
    for c in sorted(grouped - shown):
        print('В GROUPS есть, в снимке нет:', c, file=sys.stderr)
    arrow = {'m2o': '}o--||', 'm2o?': '}o--o|', 'm2m': '}o--o{'}
    parts = []
    for title, cs in groups:
        mine = {c for c, _ in cs}
        mine_es = [(a, b, f, k) for a, b, f, k in es if a in mine and b in mine]
        lines = [f'{a} {arrow[k]} {b} : "{f}"' for a, b, f, k in mine_es]
        for c, wanted in cs:
            if wanted:
                lines += block(snap, c, wanted)
            elif c in shown and not any(c in (a, b) for a, b, _, _ in mine_es):
                lines.append(c)
        parts.append(f'**{title}**\n\n' + mermaid(lines))
    head = ('Схемы собраны скриптом `scripts/directus-schema.py` из снимка `docs/directus-snapshot.json` — '
            'руками не править. Подпись линии — поле, в котором хранится связь. '
            '`}o--||` — многие к одному, поле обязательно; `}o--o|` — многие к одному, поле может быть пустым; '
            '`}o--o{` — многие ко многим (через служебную таблицу). На схеме темы — только связи между '
            'её коллекциями; `works` и другие общие коллекции повторяются в нескольких темах.\n\n')
    return head + '\n'.join(parts)


def main():
    snap = fetch() if '--fetch' in sys.argv else json.loads(SNAPSHOT.read_text(encoding='utf-8'))
    ver = str(snap['data'].get('directus', ''))
    snap['data']['directus'] = ver.split('.')[0]
    SNAPSHOT.write_text(json.dumps(snap, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    doc = DOC.read_text(encoding='utf-8')
    if BEGIN not in doc or END not in doc:
        sys.exit(f'в {DOC} нет меток {BEGIN} … {END}')
    pre, rest = doc.split(BEGIN, 1)
    _, post = rest.split(END, 1)
    DOC.write_text(pre + BEGIN + '\n' + render(snap) + END + post, encoding='utf-8')
    print('снимок:', SNAPSHOT.relative_to(ROOT), '(версия', ver, '→', snap['data']['directus'] + ');',
          'схемы:', DOC.relative_to(ROOT))


if __name__ == '__main__':
    main()
