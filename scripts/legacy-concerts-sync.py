#!/usr/bin/env python3
"""Sync concerts from the legacy concert list into Directus (events + perfs).

The legacy page (LEGACY_URL) is still maintained, so this script is meant to be
run again and again. It only ADDS: events missing from the database, and the
programme (perfs) of events that have no perfs at all. Existing records are
never changed; differences are listed in the report for a person to decide.

Legacy markup of a programme line:
    Title (First line…) [year]          a song by M. Shcherbakov
    First line… [year]                  untitled song (matched by incipit)
    + Title …                           premiere          -> perfs.is_premiere
    (соло) Title …                      in a duet concert, without M. Starodubtsev (no with_mls)
    (М. Стародубцев) Title …            sung by him alone -> perfs.sings_mls_only
    § Title … [year] (стихи)            read as a poem    -> perfs.is_poem
    … (фонограмма)                      to a backing track -> perfs.sings_with_minus
    * Title (First line…) (Author)      someone else's song (works.author)
    ???                                 unknown song: skipped, reported
    ---                                 interval
Event flags (data-flags): D duet, P premiere, F abroad, H home concert,
L programme known, I photo, C someone else's songs in the programme.

Manual fixes live in scripts/legacy-concerts-sync.json and are kept between runs:
    "works":  {"<legacy title as on the page>": "<works.id>"}   unmatched songs
    "events": {"<event id>": {"<field>": <value>, ...}}           field overrides
    "skip":   ["<event id>", ...]                                  never create
    "db_only": ["<event id>", ...]   known to be in the database only, not reported

Usage:
    scripts/legacy-concerts-sync.py                  # report only, public token
    scripts/legacy-concerts-sync.py --since 2021     # default: 2024
    scripts/legacy-concerts-sync.py --file page.html # local copy of the page
    DIRECTUS_ADMIN_TOKEN=... scripts/legacy-concerts-sync.py --apply
The public token cannot see draft events; with --apply the admin token is used
for reading too, so a draft event is not created twice.
"""
import argparse
import datetime
import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request

BASE = os.environ.get("DIRECTUS_URL", "https://db.sch.com.ru")
LEGACY_URL = "https://lambda.mkshch.com/fans/utf/concerts.html"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP_FILE = os.path.join(ROOT, "scripts", "legacy-concerts-sync.json")
UA = "schugo-legacy-concerts-sync"
AUTHOR = "Щербаков"

COUNTRIES = {"США", "Израиль", "Германия", "Франция", "Канада", "Беларусь", "Украина",
             "Латвия", "Литва", "Эстония", "Великобритания", "Чехия", "Финляндия",
             "Нидерланды", "Бельгия", "Швейцария", "Австрия", "Австралия", "Казахстан",
             "Грузия", "Армения", "Кипр", "Черногория", "Сербия", "Италия", "Испания",
             "Польша", "Болгария", "Норвегия", "Швеция", "Дания", "Ирландия"}
TOWN_COUNTRY = {"Минск": "Беларусь", "Киев": "Украина", "Харьков": "Украина",
                "Одесса": "Украина", "Рига": "Латвия", "Таллин": "Эстония",
                "Вильнюс": "Литва", "Хайфа": "Израиль", "Иерусалим": "Израиль",
                "Тель-Авив": "Израиль", "Алматы": "Казахстан", "Тбилиси": "Грузия"}
WEEKDAYS = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]
TAIL = re.compile(r"^(дневной|вечерний|домашний( концерт)?( у .*)?|второй акт.*|"
                  r"дуэт \([^)]*\)|(\d+ )?премьер[аы]|с Ю\. Кимом)$")
# keyboard words in «дуэт (…)» -> perfs.mls_instrument (None: kind of keyboard unknown)
KEYBOARDS = {"клавиши": None, "рояль": "рояль"}


# ─── reading ─────────────────────────────────────────────────────────────────
def http_get(url, token=None):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def api(path, token, method="GET", body=None):
    req = urllib.request.Request(BASE + path, method=method, headers={
        "User-Agent": UA, "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"})
    data = json.dumps(body).encode() if body is not None else None
    try:
        with urllib.request.urlopen(req, data=data, timeout=60) as r:
            raw = r.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        sys.exit(f"{method} {path}: HTTP {e.code} {e.read().decode()[:500]}")


def items(collection, token, **params):
    params.setdefault("limit", "-1")
    return api(f"/items/{collection}?" + urllib.parse.urlencode(params), token)["data"]


def public_token():
    with open(os.path.join(ROOT, "config/_default/params.json.example")) as f:
        t = json.load(f)["directus"]["token"]
    return t.split("access_token=", 1)[-1]


# ─── legacy page ─────────────────────────────────────────────────────────────
def norm(s):
    s = (s or "").lower().replace("ё", "е")
    return re.sub(r"[^\w]+", " ", s).strip()


def parse_place(rest, flags):
    """'США, Kensington, MD, клуб "X", домашний концерт' -> fields; tails dropped."""
    parts = [p.strip() for p in re.split(r",\s*(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)", rest) if p.strip()]
    notes = [p for p in parts if TAIL.match(p)]
    parts = [p for p in parts if not TAIL.match(p)]
    country = state = town = None
    if parts and parts[0] in COUNTRIES:
        country = parts.pop(0)
    if parts:
        town = parts.pop(0)
    if country == "США" and parts and re.fullmatch(r"[A-Z]{2}", parts[0]):
        state = parts.pop(0)
    if not country:
        country = TOWN_COUNTRY.get(town) or (None if "F" in flags else "Россия")
    return {"country": country, "state": state, "town": town,
            "place": ", ".join(parts) or None}, notes


def parse_line(raw):
    t = html.unescape(re.sub(r"<[^>]+>", "", raw)).strip()
    if not t:
        return None
    if t == "---":
        return {"break": True}
    s = {"raw": t, "premiere": False, "poem": False, "minus": False, "cover": False}
    if t.startswith("+"):
        s["premiere"], t = True, t[1:].strip()
    if t.startswith("§"):
        s["poem"], t = True, t[1:].strip()
    if t.startswith("*"):
        s["cover"], t = True, t[1:].strip()
    if t.startswith("(соло)"):  # in a duet concert: without M. Starodubtsev
        s["solo"], t = True, t[len("(соло)"):].strip()
    if t.startswith("(М. Стародубцев)"):  # sung by M. Starodubtsev alone
        s["mls_only"], t = True, t[len("(М. Стародубцев)"):].strip()
    if t.endswith("(фонограмма)"):
        s["minus"], t = True, t[: -len("(фонограмма)")].strip()
    if t.endswith("(стихи)"):
        s["poem"], t = True, t[: -len("(стихи)")].strip()
    if t.startswith("???"):
        s["unknown"] = True
        return s
    m = re.search(r"\s*\[(\d{4})\]\s*$", t)
    if m:
        s["year"], t = m.group(1), t[: m.start()]
    elif s["cover"]:
        m = re.search(r"\s*\(([^()]*)\)\s*$", t)
        if m:
            s["author"], t = m.group(1), t[: m.start()]
    m = re.match(r"(.*?)\s*\((.*)\)\s*$", t)
    if m:
        s["title"], s["first_line"] = m.group(1), m.group(2)
    else:
        s["title"], s["first_line"] = t, None
    return s


def parse_legacy(page, since):
    out = []
    for year, flags, body in re.findall(
            r'<details class="(\d{4})" data-flags="([^"]*)">(.*?)</details>', page, re.S):
        if int(year) < since:
            continue
        summary = re.search(r"<summary>(.*?)</summary>", body, re.S).group(1)
        summary = html.unescape(re.sub(r"<[^>]+>", "", summary)).strip()
        m = re.match(r"(\?\?|\d\d)\.(\?\?|\d\d)\.(\d{4})\s+(\S+)\s+–\s+(.*)$", summary)
        if not m:
            out.append({"error": f"не разобрана строка: {summary}"})
            continue
        d, mo, y, dw, rest = m.groups()
        fields, notes = parse_place(rest, flags)
        de = "дневной" if "дневной" in notes else "вечерний" if "вечерний" in notes else None
        eid = f"L{y}-{mo}-{d}" + ("-1" if de == "дневной" else "-2" if de == "вечерний" else "")
        exact = "?" not in d + mo
        duet = re.search(r"дуэт \(([^)]*)\)", rest)
        instruments = [i.strip() for i in duet.group(1).split(",")] if duet else []
        keyboard = any(i in KEYBOARDS for i in instruments)
        ev = {"id": eid, "date": f"{y}-{mo}-{d}" if exact else None, "year": int(y),
              "dw": dw if exact else None, "day_evening": de, "is_studio": False,
              "status": "published", "is_home": True if "H" in flags else None,
              "with_mls": "D" in flags, "plays_mls_keyboard": keyboard,
              "date_approximate": not exact, **fields}
        ol = re.search(r"<ol>(.*?)</ol>", body, re.S)
        songs = [x for x in (parse_line(l) for l in (ol.group(1).splitlines() if ol else [])) if x]
        # keyboards on every song only when the keyboard is the only instrument
        # («дуэт (гитара, рояль)»: which songs had the piano is unknown)
        out.append({"event": ev, "flags": flags, "summary": summary, "notes": notes,
                    "keyboard_all": instruments[0] if keyboard and len(instruments) == 1 else None,
                    "songs": songs, "grey": "color: #888" in body.split("</summary>")[0]})
    return out


# ─── matching songs to works ─────────────────────────────────────────────────
class Works:
    def __init__(self, works, manual):
        self.works, self.manual = works, manual
        self.by_name, self.by_id = {}, {w["id"]: w for w in works}
        for w in works:
            self.by_name.setdefault(norm(w.get("name")), []).append(w)

    def match(self, s):
        if s["raw"] in self.manual:
            return self.by_id.get(self.manual[s["raw"]]), "словарь"
        title, fl = s.get("title") or "", s.get("first_line")
        if norm(title) == "без названия" and fl:
            title, fl = fl, fl
        def by_author(ws):  # someone else's song («*») only among others' works, and vice versa
            return [w for w in ws if ((w.get("author") or AUTHOR) == AUTHOR) != s["cover"]]
        cands = by_author(self.by_name.get(norm(title), []))
        probe = norm(fl or title)[:24]
        if not cands and probe:
            cands = by_author([w for w in self.works
                               if norm(w.get("incipit")) and (norm(w["incipit"]).startswith(probe)
                                                             or probe.startswith(norm(w["incipit"])[:24]))])
        if len(cands) > 1 and s.get("year"):
            cands = [w for w in cands if str(w.get("date") or "")[:4] == s["year"]] or cands
        if len(cands) > 1 and fl:
            cands = [w for w in cands if norm(w.get("incipit")).startswith(norm(fl)[:12])] or cands
        if len(cands) == 1:
            return cands[0], "авто"
        return None, "несколько" if cands else "нет"


# ─── plan ────────────────────────────────────────────────────────────────────
def build_perfs(ev, songs, works, problems, keyboard_all=None):
    perfs, num, after_break = [], 0, False
    seen = set()
    for s in songs:
        if s.get("break"):
            after_break = True
            if perfs:
                perfs[-1]["is_last_before_break"] = True
            continue
        if s.get("unknown"):
            problems.append(f"{ev['id']}: «{s['raw']}» — песня не опознана на старой странице, пропущена")
            continue
        w, how = works.match(s)
        if not w:
            problems.append(f"{ev['id']}: «{s['raw']}» — в works {'несколько кандидатов' if how == 'несколько' else 'не найдено'}")
            continue
        pid = f"{ev['id']}_{w['id']}"
        if pid in seen:
            problems.append(f"{ev['id']}: «{s['raw']}» исполнена повторно — id {pid} уже занят, пропущена")
            continue
        seen.add(pid)
        num += 1
        p = {"id": pid, "events_id": ev["id"], "works_id": w["id"], "num": num,
             "is_first": num == 1, "is_first_after_break": False,
             "is_premiere": s["premiere"], "is_poem": s["poem"]}
        if after_break:
            p["is_first_after_break"], after_break = True, False
        if s["minus"]:
            p["sings_with_minus"] = True
        if s.get("mls_only"):
            p["with_mls"], p["sings_mls_only"] = True, True
        elif ev.get("with_mls") and not s.get("solo"):
            p["with_mls"] = True
            if keyboard_all:
                p["plays_mls_keyboards"] = True
                if KEYBOARDS[keyboard_all]:
                    p["mls_instrument"] = KEYBOARDS[keyboard_all]
        perfs.append(p)
    if perfs:
        perfs[-1]["is_last"] = True
    return perfs


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--since", type=int, default=2024, help="first year (default 2024)")
    ap.add_argument("--file", help="local copy of the legacy page instead of downloading it")
    ap.add_argument("--apply", action="store_true", help="write to Directus (needs DIRECTUS_ADMIN_TOKEN)")
    args = ap.parse_args()

    admin = os.environ.get("DIRECTUS_ADMIN_TOKEN")
    if args.apply and not admin:
        sys.exit("--apply needs DIRECTUS_ADMIN_TOKEN in the environment")
    token = admin or public_token()
    manual = {"works": {}, "events": {}, "skip": [], "db_only": []}
    if os.path.exists(MAP_FILE):
        with open(MAP_FILE) as f:
            manual.update(json.load(f))

    page = open(args.file, encoding="utf-8").read() if args.file else http_get(LEGACY_URL).decode("utf-8")
    legacy = parse_legacy(page, args.since)
    works = Works(items("works", token, fields="id,name,incipit,author,date"), manual["works"])
    db_events = {e["id"]: e for e in items("events", token, **{
        "fields": "id,date,day_evening,country,state,town,place,is_home,with_mls,status",
        "filter[year][_gte]": str(args.since)})}
    db_perfs = {}
    for p in items("perfs", token, **{"fields": "id,events_id,works_id",
                                      "filter[events_id][year][_gte]": str(args.since)}):
        db_perfs.setdefault(p["events_id"], []).append(p)

    create_events, create_perfs, problems, diffs = [], [], [], []
    today = datetime.date.today().isoformat()
    for item in legacy:
        if "error" in item:
            problems.append(item["error"])
            continue
        ev = item["event"]
        ev.update(manual["events"].get(ev["id"], {}))
        eid = ev["id"]
        if eid in manual["skip"]:
            continue
        if ev["date_approximate"]:
            # «??.11.2024»: no id can be built from it; the event is entered by hand
            # (then put its id into "events" with the legacy id as key, or into "skip")
            same = [k for k in db_events if k.startswith(eid.split("?")[0])]
            problems.append(f"{eid}: неточная дата («{item['summary']}») — не создаётся"
                            + (f"; в базе похожие: {', '.join(same)}" if same else "")
                            + f" — добавить в skip в {os.path.basename(MAP_FILE)}")
            continue
        if ev["date"] > today:
            continue  # not yet held: announces are a separate matter
        if ev["date"] and ev["dw"] and WEEKDAYS[datetime.date.fromisoformat(ev["date"]).weekday()] != ev["dw"]:
            problems.append(f"{eid}: день недели на старой странице «{ev['dw']}» не совпадает с датой")
        if ev["country"] is None:
            problems.append(f"{eid}: страна не определена («{item['summary']}») — задать в {os.path.basename(MAP_FILE)}")
        new_perfs = build_perfs(ev, item["songs"], works, problems, item["keyboard_all"]) if "L" in item["flags"] else []
        if eid not in db_events:
            create_events.append((ev, item))
            create_perfs.extend(new_perfs)
            continue
        have = db_perfs.get(eid, [])
        if not have:
            create_perfs.extend(new_perfs)
        else:
            a = sorted(p["works_id"] or "?" for p in have)
            b = sorted(p["works_id"] for p in new_perfs)
            if a != b:
                only_db, only_legacy = set(a) - set(b), set(b) - set(a)
                diffs.append(f"{eid}: в базе {len(a)}, на старой странице {len(b)}"
                             + (f"; только в базе: {', '.join(sorted(only_db))}" if only_db else "")
                             + (f"; только на старой: {', '.join(sorted(only_legacy))}" if only_legacy else ""))
        db = db_events[eid]
        if db.get("day_evening") not in (None, "дневной", "вечерний"):
            diffs.append(f"{eid}: day_evening в базе {db['day_evening']!r} — недопустимое значение (дневной / вечерний / пусто)")
        elif db.get("day_evening") != ev.get("day_evening"):
            diffs.append(f"{eid}: day_evening в базе {db.get('day_evening')!r}, на старой странице {ev.get('day_evening')!r}")
        if bool(db.get("with_mls")) != bool(ev.get("with_mls")):
            diffs.append(f"{eid}: with_mls в базе {db.get('with_mls')!r}, на старой странице {ev.get('with_mls')!r}")
        if bool(db.get("is_home")) != bool(ev.get("is_home")):
            diffs.append(f"{eid}: is_home в базе {db.get('is_home')!r}, на старой странице {ev.get('is_home')!r}")

    legacy_ids = {i["event"]["id"] for i in legacy if "event" in i}
    for eid, e in sorted(db_events.items()):
        if eid not in legacy_ids and eid not in manual["db_only"] and eid.startswith(("L", "2")):
            diffs.append(f"{eid}: есть в базе, нет на старой странице ({e.get('date')}, {e.get('town')}, {e.get('place')})")

    # ─── report ──────────────────────────────────────────────────────────────
    print(f"Старая страница: {len(legacy)} концертов с {args.since} года; в базе событий: {len(db_events)}"
          + ("" if admin else " (публичный токен: черновики не видны)"))
    print(f"\n== Создать события: {len(create_events)}")
    for ev, item in create_events:
        n = sum(1 for p in create_perfs if p["events_id"] == ev["id"])
        flags = ", ".join(k for k in ("with_mls", "plays_mls_keyboard", "is_home", "date_approximate") if ev.get(k))
        print(f"  {ev['id']:15} {ev['country'] or '?'} | {ev['state'] or '-'} | {ev['town'] or '-'} | "
              f"{ev['place'] or '-'} | {ev['day_evening'] or '-'}{' | ' + flags if flags else ''} | исполнений: {n}"
              + (f" | хвост: {', '.join(item['notes'])}" if item["notes"] else ""))
    by_ev = {}
    for p in create_perfs:
        by_ev.setdefault(p["events_id"], []).append(p)
    existing_targets = [e for e in by_ev if e in db_events]
    print(f"\n== Создать исполнения: {len(create_perfs)} (из них у событий, которые уже есть в базе без программы: "
          f"{sum(len(by_ev[e]) for e in existing_targets)} — {', '.join(existing_targets) or 'нет'})")
    marks = sum(1 for p in create_perfs if p["is_premiere"]), sum(1 for p in create_perfs if p["is_poem"]), \
        sum(1 for p in create_perfs if p.get("sings_with_minus"))
    print(f"  премьер {marks[0]}, стихов {marks[1]}, под фонограмму {marks[2]}")
    print(f"\n== Не опознано и прочие проблемы: {len(problems)}")
    for p in problems:
        print("  " + p)
    print(f"\n== Расхождения с базой (ничего не меняется, решает человек): {len(diffs)}")
    for d in diffs:
        print("  " + d)

    if not args.apply:
        print("\nНичего не записано. Запись: DIRECTUS_ADMIN_TOKEN=... scripts/legacy-concerts-sync.py --apply")
        return
    for ev, _ in create_events:
        api("/items/events", admin, "POST", {k: v for k, v in ev.items() if v is not None})
        print("создано событие", ev["id"])
    for i in range(0, len(create_perfs), 100):
        api("/items/perfs", admin, "POST", create_perfs[i:i + 100])
    print(f"создано исполнений: {len(create_perfs)}")


if __name__ == "__main__":
    main()
