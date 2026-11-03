#!/usr/bin/env python3
"""Снимок схемы Directus и схемы связей коллекций в docs/directus.md.

Запускать после каждого изменения модели данных в Directus:

    DIRECTUS_ADMIN_TOKEN=… python3 scripts/directus-schema.py --fetch

--fetch  забрать свежий снимок (GET /schema/snapshot, нужен токен администратора
         в переменной окружения DIRECTUS_ADMIN_TOKEN) в docs/directus-snapshot.json,
         а Flows и модель прав (flows, roles, policies, access, permissions) —
         в docs/directus-export/; без него  взять уже лежащий снимок.

Дальше скрипт всегда:
  1) заменяет точную версию Directus в снимке на мажорную («11»): репозиторий
     публичный, а сам Directus версию анонимам не показывает;
  2) пересобирает в docs/directus.md чертежи Mermaid — каждый между своими метками
     <!-- schema:Тема --> и <!-- /schema:Тема -->. Текст вне меток (заголовки тем,
     пояснения автора) не трогает; порядок тем в документе можно менять руками.
     Тема из GROUPS, которой ещё нет в документе, дописывается после последней.

Какая коллекция на какой схеме — решает человек: список GROUPS ниже.
Коллекция, которой нет ни в одной группе, попадает на схему «Не распределены»,
и скрипт об этом пишет. Служебные таблицы «многие ко многим» (скрытые в Directus)
отдельно не рисуются: связь через них — одна линия }o--o{ между двумя коллекциями.
"""
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT = ROOT / 'docs' / 'directus-snapshot.json'
DOC = ROOT / 'docs' / 'directus.md'
LEGEND = 'legend'  # метки <!-- schema:legend --> … <!-- /schema:legend --> вокруг пояснения к схемам
BASE = 'https://db.sch.com.ru/'
EXPORT = ROOT / 'docs' / 'directus-export'
EXPORTS = [('flows', 'flows?limit=-1&fields=*,operations.*'),
           ('roles', 'roles?limit=-1&fields=*'),
           ('policies', 'policies?limit=-1&fields=*'),
           ('access', 'access?limit=-1&fields=*'),
           ('permissions', 'permissions?limit=-1&fields=*')]

# Порядок групп = порядок схем в документе. Линия рисуется, только если ОБЕ коллекции
# в группе, поэтому общие (works, performers, links…) вписаны в каждую тему, где нужны.
# Элемент группы — имя коллекции (пустой блок) или (имя, [поля]) — блок с этими полями
# в этом порядке; '*' вместо списка — все поля. У одной коллекции в разных группах
# поля могут быть разными. Необязательный третий элемент группы — центральная коллекция:
# тогда рисуются только её связи, без линий между остальными («с чем связана эта таблица»).
# Вместо имени центральной коллекции можно дать словарь: {'center': …, 'direction': 'LR' (слева направо),
# 'left': коллекция, которую поставить слева — её линии пишутся «от неё», и Mermaid кладёт её первой}.
GROUPS = [
    # Ядро: песня — исполнение — событие, в строку слева направо.
    ('Песня, исполнение, событие', ['works', 'perfs',
                                    ('events', ['id', 'status', 'date', 'date_approximate', 'year', 'time', 'dw',
                                                'day_evening', 'country', 'state', 'town', 'place', 'name',
                                                'is_studio'])]),
    # Коллекции песни
    ('Песни', [('works', ['name', 'sort', 'incipit', 'fincipit', 'hidden', 'date', 'edit', 'author', 'music']), 'perfs', 'books_entries', 'translations', 'recordings', 'statements', 'variants', 'works_see_also', 'comments', 'cycles_entries'], 'works'),
    ('Издания', [('works', ['id']), 
                ('books', ['id', 'series', 'name', 'fullname', 'show_on_catalogpage', 'show_on_songpage']), 
                'book_sets', 
                ('books_entries',['works_id', 'books_id', 'page']), 
                ]),
    ('Комментарии', ['works', ('comments',['body', 'work_id', 'sort_order']), 'works_see_also']),
    ('Варианты', ['works', 'variants', 'perfs', 'books_entries']),
    ('Переводы', ['works', 'translations', 'languages', 'translators']),
    ('Циклы', ['works', 'cycles', 'cycles_entries']),
    ('Высказывания', ['works', 'statements']),
    ('Исполнители', ['works', 'releases', 'recordings', 'performers', 'links']),
    # Коллекции события
    ('События', [('events', ['id', 'status', 'date', 'date_approximate', 'year', 'time', 'dw', 'day_evening',
                             'country', 'state', 'town', 'place', 'name', 'is_studio', 'set_id']),
                 'announces', 'log_entries', 'perfs', 'performers', 'sets']),
    ('Исполнения', [('perfs', ['id', 'events_id', 'works_id', 'variants_id', 'num', 'note']),
                    'events', 'works', 'variants', 'performers', 'sets_entries'], 'perfs'),
    ('Диски', [('works', ['id']), ('perfs', ['events_id', 'works_id', 'num']), ('sets',['title', 'year', 'ignore_in_catalogue']), ('sets_entries', ['perfs_id', 'sets_id', 'num']), 'disk_formats']),
    ('Лог', ['events', 'log_entries']),
]


def get(path):
    tok = os.environ.get('DIRECTUS_ADMIN_TOKEN')
    if not tok:
        sys.exit('нет токена: задайте DIRECTUS_ADMIN_TOKEN (снимок схемы и права отдаются только администратору)')
    req = urllib.request.Request(BASE + path, headers={'Authorization': 'Bearer ' + tok})
    return json.load(urllib.request.urlopen(req))


def fetch():
    return get('schema/snapshot')


def export_settings():
    """Flows и модель прав — в docs/directus-export/*.json, ключи отсортированы ради читаемого diff.

    Сознательно НЕ выгружаются directus_settings (ключи сервисов, вписанные в Studio, лежат там
    открытым текстом) и directus_users/sessions/activity/revisions (учётные данные и история).
    Секреты во Flows — только через {{$env.X}}; перед коммитом смотреть diff flows.json.
    """
    EXPORT.mkdir(exist_ok=True)
    for name, path in EXPORTS:
        data = get(path)['data']
        (EXPORT / f'{name}.json').write_text(
            json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print('Flows и права:', EXPORT.relative_to(ROOT))


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
    """Легенда и [(название темы, чертёж mermaid)] в порядке GROUPS."""
    es, hidden = edges(snap)
    shown = {c['collection'] for c in snap['data']['collections']} - hidden
    def opts(g):
        o = g[2] if len(g) > 2 else {}
        return {'center': o} if isinstance(o, str) else o
    norm = [(g[0], [(c, None) if isinstance(c, str) else (c[0], c[1]) for c in g[1]], opts(g)) for g in GROUPS]
    grouped = {c for _, cs, _ in norm for c, _ in cs}
    groups = list(norm)
    rest = sorted(shown - grouped)
    if rest:
        print('Не распределены по схемам (добавьте в GROUPS):', ', '.join(rest), file=sys.stderr)
        groups.append(('Не распределены', [(c, None) for c in rest], {}))
    for c in sorted(grouped - shown):
        print('В GROUPS есть, в снимке нет:', c, file=sys.stderr)
    arrow = {'m2o': '}o--||', 'm2o?': '}o--o|', 'm2m': '}o--o{'}
    parts = []
    flip = {'m2o': '||--o{', 'm2o?': '|o--o{', 'm2m': '}o--o{'}  # та же связь, записанная «от одной стороны»
    for title, cs, o in groups:
        center, left = o.get('center'), o.get('left')
        mine = {c for c, _ in cs}
        mine_es = [(a, b, f, k) for a, b, f, k in es if a in mine and b in mine
                   and (center is None or center in (a, b))]
        lines = ['direction ' + o['direction']] if o.get('direction') else []
        lines += [f'{b} {flip[k]} {a} : "{f}"' if b == left else f'{a} {arrow[k]} {b} : "{f}"'
                  for a, b, f, k in mine_es]
        for c, wanted in cs:
            if wanted:
                lines += block(snap, c, wanted)
            elif c in shown and not any(c in (a, b) for a, b, _, _ in mine_es):
                lines.append(c)
        parts.append((title, mermaid(lines)))
    legend = ('Чертежи между метками `<!-- schema:… -->` собирает скрипт `scripts/directus-schema.py` '
              'из снимка `docs/directus-snapshot.json` — их руками не править; текст вне меток скрипт не трогает. '
              'Подпись линии — поле, в котором хранится связь. '
              'В блоке таблицы каждая строка — поле: сначала тип Directus (`text`, `string`, `integer`, '
              '`boolean`…), затем имя поля, затем `PK` (первичный ключ) или `FK` (поле связи), если поле — ключ. '
              '`}o--||` — многие к одному, поле обязательно; `}o--o|` — многие к одному, поле может быть пустым; '
              '`}o--o{` — многие ко многим (через служебную таблицу). На схеме темы — только связи между '
              'её коллекциями; `works` и другие общие коллекции повторяются в нескольких темах.\n')
    return legend, parts


def block_re(name):
    # метка — только целая строка, чтобы пример метки в тексте не считался меткой
    return re.compile(r'(^<!-- schema:' + re.escape(name) + r' -->\n).*?(^<!-- /schema:' + re.escape(name)
                      + r' -->$)', re.S | re.M)


def main():
    snap = fetch() if '--fetch' in sys.argv else json.loads(SNAPSHOT.read_text(encoding='utf-8'))
    if '--fetch' in sys.argv:
        export_settings()
    ver =str(snap['data'].get('directus', ''))
    snap['data']['directus'] = ver.split('.')[0]
    SNAPSHOT.write_text(json.dumps(snap, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    doc = DOC.read_text(encoding='utf-8')
    legend, parts = render(snap)
    if not block_re(LEGEND).search(doc):
        sys.exit(f'в {DOC} нет меток <!-- schema:{LEGEND} --> … <!-- /schema:{LEGEND} -->')
    # Заменяется только содержимое между парными метками; всё вокруг — текст автора.
    for name, body in [(LEGEND, legend)] + parts:
        rx = block_re(name)
        if rx.search(doc):
            doc = rx.sub(lambda m: m.group(1) + body + m.group(2), doc, count=1)
        else:
            # Новая тема: дописать заголовок и чертёж после последнего чертежа.
            last = list(re.finditer(r'^<!-- /schema:[^>]+ -->$', doc, re.M))[-1]
            new = f'\n\n**{name}**\n\n<!-- schema:{name} -->\n{body}<!-- /schema:{name} -->'
            doc = doc[:last.end()] + new + doc[last.end():]
            print('Новая схема дописана в конец:', name, file=sys.stderr)
    known = {LEGEND} | {n for n, _ in parts}
    for m in re.finditer(r'^<!-- schema:([^>]+?) -->$', doc, re.M):
        if m.group(1) not in known:
            print(f'В документе есть схема «{m.group(1)}», которой нет в GROUPS — удалите её вручную',
                  file=sys.stderr)
    DOC.write_text(doc, encoding='utf-8')
    print('снимок:', SNAPSHOT.relative_to(ROOT), '(версия', ver, '→', snap['data']['directus'] + ');',
          'схемы:', DOC.relative_to(ROOT))


if __name__ == '__main__':
    main()
