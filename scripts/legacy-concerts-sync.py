#!/usr/bin/env python3
"""Sync concerts from the legacy concert list into Directus (events + perfs).

The legacy page (LEGACY_URL) is still maintained, so this script is meant to be
run again and again. It only ADDS: events missing from the database, and the
programme (perfs) of events that have no perfs at all. Existing records are
never changed; differences are listed in the report for a person to decide.

Legacy markup of a programme line:
    Title (First line…) [year]          a song by M. Shcherbakov
    First line… [year]                  untitled song (matched by incipit)
    - Title …                           early song outside the main collection (italic); marker dropped
    + Title …                           premiere          -> perfs.is_premiere
    (соло) Title …                      in a duet concert, without M. Starodubtsev (no with_mls)
    (М. Стародубцев) Title …            sung by him alone -> perfs.sings_mls_only
    § Title … [year] (стихи)            read as a poem    -> perfs.is_poem
    … (фонограмма)                      to a backing track -> perfs.sings_with_minus
    … [year] (недопел) / (пропущен куплет)   not sung in full -> perfs.sings_incomplete
    … [year] (обновлённый текст) / (аранжировка …)   noted, nothing written
    --- (or «--- Д. Фиш (скрипка), …»)  interval (and who joins the next act)
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
    "no_fix":  ["<event id>", ...]   --fix leaves the event and its songs alone
    "perfs":   {"<perf id>": {"<field>": <value>, ...}}   known better than the page
               (e.g. which act had the piano); --fix writes them over its own corrections
    "event_fixes": {"<event id>": {"<field>": <value>, ...}}   the same for events (e.g. place)
    "approx":  {"<summary of a concert with an inexact date, as on the page>": "<event id>"}
               ties it to an event (existing, or created with the date from "events")
    "reorder": ["<event id>", ...]   same songs, the page's order is the right one: the perfs'
               own num values are given out again in the page's order (with --apply)
    "complete": ["<event id>", ...]   programme entered only in part: the songs it lacks are
               added (with --apply), if all it has matches the page
    "delete_perfs": ["<perf id>", ...]   wrong perfs, deleted with --apply (e.g. another
               concert's programme mixed in when the database was first filled)
An "events" override changes what the page is taken to say, so with --fix it
also steers the correction (e.g. {"L2014-06-08": {"is_home": false}}).

--fix (with --apply: writes) corrects fields of events already in the database
by the page, see plan_fixes(); it never creates anything.

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
import difflib
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
                "Таллинн": "Эстония", "Вильнюс": "Литва", "Хайфа": "Израиль", "Иерусалим": "Израиль",
                "Тель-Авив": "Израиль", "Алматы": "Казахстан", "Тбилиси": "Грузия"}
WEEKDAYS = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]
TAIL = re.compile(r"^(дневной|девной|вечерний|домашний( концерт)?( у .*)?|второй акт.*|"
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
    if t.startswith("---"):  # interval; «--- Д. Фиш (скрипка), Г. Кац (гитара)» — who joins the next act
        return {"break": True, "after": t[3:].strip() or None}
    s = {"raw": t, "premiere": False, "poem": False, "minus": False, "cover": False}
    if t.startswith("- "):  # an early song outside the main collection (italic on the page)
        s["early"], t = True, t[2:].strip()
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
    # notes after the year, in any order: «[1986] (недопел)», «[2025] (обновлённый текст)»
    while True:
        m = re.search(r"\s*\((фонограмма|стихи|недопел|пропущен куплет|обновлённый текст|аранжировка [^()]*)\)\s*$", t)
        if not m:
            break
        note, t = m.group(1), t[: m.start()]
        if note == "фонограмма":
            s["minus"] = True
        elif note == "стихи":
            s["poem"] = True
        elif note in ("недопел", "пропущен куплет"):
            s["incomplete"] = True
        else:
            s.setdefault("notes", []).append(note)
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
        de = "дневной" if "дневной" in notes or "девной" in notes else "вечерний" if "вечерний" in notes else None
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
        # the map is keyed by the whole line as on the page, or by the title alone («Ей 28 лет…»)
        key = s["raw"] if s["raw"] in self.manual else s.get("title") if s.get("title") in self.manual else None
        if key:
            return self.by_id.get(self.manual[key]), "словарь"
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
UNKNOWN = "unknown"  # «???»: a perf without a song, id <event>_unknown


def legacy_seq(ev, songs, works, problems):
    """The page's programme as a list of entries: song (UNKNOWN for «???», None if not found
    in works — reported), the act it is in, and whether it is optional.

    A song the page lists twice is taken twice only if one of the two is marked «(недопел)»
    (not sung in full, then sung again). Otherwise the repeat is doubtful (the page has such
    errors) and the database keeps one performance: all occurrences are optional, and the one
    the database has (by alignment) is the one taken."""
    seq, act = [], 0
    for s in songs:
        if s.get("break"):
            act += 1
            continue
        if s.get("unknown"):
            work = UNKNOWN
        else:
            w, how = works.match(s)
            work = w["id"] if w else None
            if not w:
                problems.append(f"{ev['id']}: «{s['raw']}» — в works "
                                f"{'несколько кандидатов' if how == 'несколько' else 'не найдено'}")
        seq.append({"work": work, "song": s, "act": act, "optional": False})
    by_work = {}
    for x in seq:
        if x["work"] and x["work"] != UNKNOWN:
            by_work.setdefault(x["work"], []).append(x)
    for xs in by_work.values():
        if len(xs) > 1 and not any(x["song"].get("incomplete") for x in xs):
            for x in xs:
                x["optional"] = True
    return seq


def perf_id(eid, work, n):
    return f"{eid}_{work}" + (f"_{n}" if n > 1 else "")


def align(seq, have):
    """Match the database programme (in num order) to the page's.

    Returns (entries, extra): entries — the programme as it should be, in the page's order,
    each {"x": page entry, "p": database perf or None (missing)}; a doubtful repeat (optional)
    is kept once: where the database has it, else at its first place. extra — database perfs
    with no place on the page. Entries with a song not in works make it None, None."""
    if any(not x["work"] for x in seq):
        return None, None
    dbs = sorted(have, key=lambda p: p.get("num") or 0)
    sm = difflib.SequenceMatcher(a=[x["work"] for x in seq], b=[p["works_id"] or UNKNOWN for p in dbs],
                                 autojunk=False)
    matched = {}
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            matched[blk.a + k] = dbs[blk.b + k]
    # a doubtful repeat the alignment left out: the database perf goes to the nearest of its places
    for b_rank, p in enumerate(dbs):
        if p["id"] in {q["id"] for q in matched.values()}:
            continue
        places = [i for i, x in enumerate(seq) if x["optional"] and x["work"] == (p["works_id"] or UNKNOWN)]
        if places and not any(i in matched for i in places):
            matched[min(places, key=lambda i: abs(i - b_rank))] = p
    extra = [p for p in dbs if p["id"] not in {q["id"] for q in matched.values()}]
    entries, done = [], set()
    for i, x in enumerate(seq):
        if x["optional"]:
            if x["work"] in done:
                continue
            if i not in matched and any(j in matched for j, y in enumerate(seq) if y["work"] == x["work"]):
                continue  # the database has this song at its other place
            done.add(x["work"])
        entries.append({"x": x, "p": matched.get(i)})
    return entries, extra


def with_breaks(entries):
    """Interval flags of the programme as it should be (an omitted repeat may stand at an act's edge)."""
    for k, e in enumerate(entries):
        e["first"], e["last"] = k == 0, k == len(entries) - 1
        e["after_break"] = k > 0 and entries[k - 1]["x"]["act"] < e["x"]["act"]
        e["before_break"] = k + 1 < len(entries) and entries[k + 1]["x"]["act"] > e["x"]["act"]
    return entries


def build_perf(ev, e, pid, num, keyboard_all):
    """A new perf for programme entry e."""
    x, s = e["x"], e["x"]["song"]
    p = {"id": pid, "events_id": ev["id"], "works_id": None if x["work"] == UNKNOWN else x["work"],
         "num": num, "is_first": e["first"], "is_last": e["last"],
         "is_first_after_break": e["after_break"], "is_premiere": s["premiere"], "is_poem": s["poem"]}
    if e["before_break"]:
        p["is_last_before_break"] = True
    if s["minus"]:
        p["sings_with_minus"] = True
    if s.get("incomplete"):
        p["sings_incomplete"] = True
    if s.get("mls_only"):
        p["with_mls"], p["sings_mls_only"] = True, True
    elif ev.get("with_mls") and not s.get("solo"):
        p["with_mls"] = True
        if keyboard_all:
            p["plays_mls_keyboards"] = True
            if KEYBOARDS[keyboard_all]:
                p["mls_instrument"] = KEYBOARDS[keyboard_all]
    return p


def new_perfs(ev, entries, taken, keyboard_all, nums):
    """Perfs for the entries without a database perf; id — the first free of
    <event>_<song>, _2, _3… (a repeat's id may thus stand on its first performance)."""
    out = []
    for e, num in zip([e for e in entries if not e["p"]], nums):
        n = 1
        while perf_id(ev["id"], e["x"]["work"], n) in taken:
            n += 1
        pid = perf_id(ev["id"], e["x"]["work"], n)
        taken.add(pid)
        out.append(build_perf(ev, e, pid, num, keyboard_all))
    return out


def _page_order(seq, have):
    """The database perfs in the page's order, if the songs are the same (each song once,
    repeats aside); else None."""
    pool = {}
    for p in sorted(have, key=lambda p: p.get("num") or 0):
        pool.setdefault(p["works_id"] or UNKNOWN, []).append(p)
    out, used = [], set()
    for x in seq:
        if not x["work"]:
            return None
        ps = pool.get(x["work"], [])
        if x["optional"] and x["work"] in used:
            continue
        if not ps:
            if x["optional"]:
                continue
            return None
        out.append(ps.pop(0))
        used.add(x["work"])
    return out if not any(pool.values()) else None


def build_perfs(ev, seq, keyboard_all=None):
    """The whole programme of an event that has none: num 1..N."""
    entries, _ = align([x for x in seq if x["work"]], [])  # songs not in works are skipped (reported)
    entries = with_breaks(entries)
    return new_perfs(ev, entries, set(), keyboard_all, range(1, len(entries) + 1))


def missing_perfs(ev, seq, have, keyboard_all, problems, any_song=False, renumber=None):
    """Perfs to add to an event whose programme in the database lacks only repeats marked
    «(недопел)» and «???» of the page (any_song: any songs — a programme entered only in part),
    num between its neighbours. [] if nothing lacks, None if anything else differs."""
    entries, extra = align(seq, have)
    if entries is None or extra:
        return None
    lack = [k for k, e in enumerate(entries) if not e["p"]]
    if not lack:
        return []
    with_breaks(entries)
    have_works = {p["works_id"] or UNKNOWN for p in have}
    if not any_song and any(entries[k]["x"]["work"] not in have_works and entries[k]["x"]["work"] != UNKNOWN
                            for k in lack):
        return None  # a song the database lacks altogether: a real difference, not a repeat
    runs = []
    for k in lack:
        if runs and runs[-1][-1] == k - 1:
            runs[-1].append(k)
        else:
            runs.append([k])
    nums, room = {}, True
    for run in runs:
        prev = next((entries[j]["p"]["num"] for j in range(run[0] - 1, -1, -1) if entries[j]["p"]), None)
        nxt = next((entries[j]["p"]["num"] for j in range(run[-1] + 1, len(entries)) if entries[j]["p"]), None)
        if prev is None and nxt is None:
            got = list(range(1, len(run) + 1))
        elif prev is None:
            got = list(range(nxt - len(run), nxt))
        elif nxt is None:
            got = list(range(prev + 1, prev + 1 + len(run)))
        else:
            step = (nxt - prev) / (len(run) + 1)
            got = [prev + round(step * (k + 1)) for k in range(len(run))]
        if len(set(got)) < len(got) or min(got) < 1 or (prev is not None and min(got) <= prev) \
                or (nxt is not None and max(got) >= nxt):
            room = False
        nums.update(zip(run, got))
    taken = {p["id"] for p in have}
    if room:
        return new_perfs(ev, entries, taken, keyboard_all, [nums[k] for k in lack])
    if not any_song:
        problems.append(f"{ev['id']}: между номерами нет места для недостающих исполнений, не добавлено")
        return []
    # a programme numbered 1..N: number it anew by the page; existing perfs through renumber
    for k, e in enumerate(entries):
        if e["p"] and e["p"].get("num") != k + 1:
            renumber.append({"id": e["p"]["id"], "num": k + 1})
    return new_perfs(ev, entries, taken, keyboard_all, [k + 1 for k in lack])


def plan_fixes(ev, item, db, have, seq):
    """--fix: field corrections of an event already in the database, by the legacy page.

    Only what the page states explicitly is set; nothing it is silent about is cleared:
    events: is_home / with_mls / plays_mls_keyboard set when the page says so; a day_evening
            that is not a valid value is replaced by the page's one;
    perfs (only if the programme in the database has the same songs as the page):
            is_first / is_last / is_last_before_break / is_first_after_break / sings_incomplete
            set; a «(соло)» song loses with_mls and
            plays_mls_keyboards; in a keyboard-only duet a song with M. Starodubtsev gets
            plays_mls_keyboards and, if empty, mls_instrument («рояль»).
    Songs without M. Starodubtsev in the database that the page does not mark are left alone:
    for early concerts the database knows more solos than the page.
    Returns (event patch, [perf patch], [note])."""
    patch, notes = {}, []
    for f in ("is_home", "with_mls", "plays_mls_keyboard"):
        if ev.get(f) and not db.get(f):
            patch[f] = True
    if db.get("day_evening") not in (None, "дневной", "вечерний"):
        patch["day_evening"] = ev.get("day_evening")
        notes.append(f"day_evening {db['day_evening']!r} → {ev.get('day_evening')!r}")

    perf_patches = []
    entries, extra = align(seq, have)
    if entries is None or extra or any(not e["p"] for e in entries):
        return patch, perf_patches, notes + ["программа расходится со старой страницей — флаги песен не правятся"]
    for e in with_breaks(entries):
        p, s, pp = e["p"], e["x"]["song"], {}
        for flag, key in (("is_first", "first"), ("is_last", "last"),
                          ("is_last_before_break", "before_break"), ("is_first_after_break", "after_break")):
            if e[key] and not p.get(flag):
                pp[flag] = True
        if s.get("incomplete") and not p.get("sings_incomplete"):
            pp["sings_incomplete"] = True
        if s.get("solo"):
            if p.get("with_mls"):
                pp["with_mls"] = False
            if p.get("plays_mls_keyboards"):
                pp["plays_mls_keyboards"] = False
        elif item["keyboard_all"] and p.get("with_mls") and not s.get("mls_only"):
            if not p.get("plays_mls_keyboards"):
                pp["plays_mls_keyboards"] = True
            if KEYBOARDS[item["keyboard_all"]] and not p.get("mls_instrument"):
                pp["mls_instrument"] = KEYBOARDS[item["keyboard_all"]]
        if pp:
            perf_patches.append({"id": p["id"], **pp})
    return patch, perf_patches, notes


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--since", type=int, default=2024, help="first year (default 2024)")
    ap.add_argument("--file", help="local copy of the legacy page instead of downloading it")
    ap.add_argument("--apply", action="store_true", help="write to Directus (needs DIRECTUS_ADMIN_TOKEN)")
    ap.add_argument("--only", help="comma-separated event ids: report and write only these events")
    ap.add_argument("--fix", action="store_true",
                    help="correct fields of events already in the database instead of creating (see plan_fixes)")
    args = ap.parse_args()

    admin = os.environ.get("DIRECTUS_ADMIN_TOKEN")
    if args.apply and not admin:
        sys.exit("--apply needs DIRECTUS_ADMIN_TOKEN in the environment")
    token = admin or public_token()
    manual = {"works": {}, "events": {}, "skip": [], "db_only": [], "no_fix": [], "perfs": {}, "event_fixes": {},
              "approx": {}, "delete_perfs": [], "complete": [], "reorder": []}
    if os.path.exists(MAP_FILE):
        with open(MAP_FILE) as f:
            manual.update(json.load(f))

    page = open(args.file, encoding="utf-8").read() if args.file else http_get(LEGACY_URL).decode("utf-8")
    legacy = parse_legacy(page, args.since)
    works = Works(items("works", token, fields="id,name,incipit,author,date"), manual["works"])
    db_events = {e["id"]: e for e in items("events", token, **{
        "fields": "id,date,day_evening,country,state,town,place,is_home,with_mls,plays_mls_keyboard,status",
        "filter[year][_gte]": str(args.since)})}
    db_perfs = {}
    # fields --fix compares, plus those named in the map's "perfs"; note is not visible to the public token
    perf_fields = {"id", "events_id", "works_id", "num", "with_mls", "plays_mls_keyboards", "mls_instrument",
                   "plays_mls_guitar", "is_last_before_break", "is_first_after_break",
                   "is_first", "is_last", "sings_incomplete"}
    perf_fields |= {k for v in manual["perfs"].values() for k in v}
    hidden = set() if admin else {"note"}
    for p in items("perfs", token, **{"fields": ",".join(sorted(perf_fields - hidden)),
                                      "filter[events_id][year][_gte]": str(args.since)}):
        db_perfs.setdefault(p["events_id"], []).append(p)

    # perfs listed for deletion: compared as if already deleted
    only = set(args.only.split(",")) if args.only else None
    doomed = set(manual["delete_perfs"])
    delete_perfs = [p["id"] for e, ps in db_perfs.items() for p in ps
                    if p["id"] in doomed and (not only or e in only)]
    for e in db_perfs:
        db_perfs[e] = [p for p in db_perfs[e] if p["id"] not in doomed]

    create_events, create_perfs, problems, diffs = [], [], [], []
    fixes = []  # (event id, event patch, [perf patch], [note])
    added_to = []  # events with a programme that get repeats / «???» added
    renumber = []  # {"id", "num"}: perfs renumbered («complete» without room, «reorder»)
    reordered = []
    seen_summaries = {}
    today = datetime.date.today().isoformat()
    for item in legacy:
        if "error" in item:
            problems.append(item["error"])
            continue
        ev = item["event"]
        if ev["date_approximate"]:
            # several concerts can share one summary («??.??.1989 ?? – Москва, МЭИ (малый зал)» ×3):
            # then the key is «summary#N», N — its place among them on the page, from 1
            seen_summaries[item["summary"]] = seen_summaries.get(item["summary"], 0) + 1
            key = f"{item['summary']}#{seen_summaries[item['summary']]}"
            mapped = manual["approx"].get(key) or manual["approx"].get(item["summary"])
            if mapped:
                ev["id"] = mapped
        else:
            mapped = None
        ev.update(manual["events"].get(ev["id"], {}))
        eid = ev["id"]
        if eid in manual["skip"] or (only and eid not in only):
            continue
        if ev["date_approximate"] and not mapped:
            # «??.11.2024»: no id can be built from it; the event is entered by hand
            # (then put its id into "events" with the legacy id as key, or into "skip")
            same = [k for k in db_events if k.startswith(eid.split("?")[0])]
            problems.append(f"{eid}: неточная дата («{item['summary']}») — не создаётся"
                            + (f"; в базе похожие: {', '.join(same)}" if same else "")
                            + f" — добавить в skip в {os.path.basename(MAP_FILE)}")
            continue
        if (ev["date"] or "") > today:
            continue  # not yet held: announces are a separate matter
        if ev["date_approximate"] and not ev["date"] and eid not in db_events:
            problems.append(f"{eid}: неточная дата — для создания задать date в events в {os.path.basename(MAP_FILE)}")
            continue
        if ev["date"] and ev["dw"] and WEEKDAYS[datetime.date.fromisoformat(ev["date"]).weekday()] != ev["dw"]:
            problems.append(f"{eid}: день недели на старой странице «{ev['dw']}» не совпадает с датой")
        if ev["country"] is None:
            problems.append(f"{eid}: страна не определена («{item['summary']}») — задать в {os.path.basename(MAP_FILE)}")
        seq = legacy_seq(ev, item["songs"], works, problems) if "L" in item["flags"] else []
        if eid not in db_events:
            create_events.append((ev, item))
            create_perfs.extend(build_perfs(ev, seq, item["keyboard_all"]))
            continue
        have = db_perfs.get(eid, [])
        add = missing_perfs(ev, seq, have, item["keyboard_all"], problems,
                            eid in manual["complete"], renumber) if have else None
        if not have:
            create_perfs.extend(build_perfs(ev, seq, item["keyboard_all"]))
        elif add:
            create_perfs.extend(add)
            added_to.append(eid)
        elif add is None and eid in manual["reorder"]:
            want = _page_order(seq, have)
            if want is None:
                diffs.append(f"{eid}: в списке reorder, но набор песен отличается от старой страницы")
            else:
                nums = sorted(p.get("num") or 0 for p in have)
                renumber.extend({"id": p["id"], "num": n} for p, n in zip(want, nums) if p.get("num") != n)
                reordered.append(eid)
        elif add is None:
            entries, extra = align(seq, have)
            if entries is None:
                diffs.append(f"{eid}: на старой странице есть песни, не найденные в works — сравнить нельзя")
            else:
                only_legacy = [e["x"]["work"] for e in entries if not e["p"]]
                only_db = [p["works_id"] or UNKNOWN for p in extra]
                moved = [w for w in only_db if w in only_legacy]
                for w in moved:
                    only_db.remove(w)
                    only_legacy.remove(w)
                place = lambda w: (next(k for k, e in enumerate(entries) if e["x"]["work"] == w) + 1,
                                   next(k for k, p in enumerate(sorted(have, key=lambda p: p.get("num") or 0))
                                        if (p["works_id"] or UNKNOWN) == w) + 1)
                diffs.append(f"{eid}: в базе {len(have)}, на старой странице {len(entries)}"
                             + (f"; только в базе: {', '.join(only_db)}" if only_db else "")
                             + (f"; только на старой: {', '.join(only_legacy)}" if only_legacy else "")
                             + (f"; другое место: " + ", ".join(f"{w} (на старой {place(w)[0]}-я, в базе {place(w)[1]}-я)"
                                                                for w in moved) if moved else ""))
        db = db_events[eid]
        if args.fix and eid not in manual["no_fix"]:
            patch, perf_patches, notes = plan_fixes(ev, item, db, have, seq)
            if patch or perf_patches or notes:
                fixes.append((eid, patch, perf_patches, notes))
        if db.get("day_evening") not in (None, "дневной", "вечерний"):
            diffs.append(f"{eid}: day_evening в базе {db['day_evening']!r} — недопустимое значение (дневной / вечерний / пусто)")
        elif db.get("day_evening") != ev.get("day_evening"):
            diffs.append(f"{eid}: day_evening в базе {db.get('day_evening')!r}, на старой странице {ev.get('day_evening')!r}")
        if bool(db.get("with_mls")) != bool(ev.get("with_mls")):
            diffs.append(f"{eid}: with_mls в базе {db.get('with_mls')!r}, на старой странице {ev.get('with_mls')!r}")
        if bool(db.get("is_home")) != bool(ev.get("is_home")):
            diffs.append(f"{eid}: is_home в базе {db.get('is_home')!r}, на старой странице {ev.get('is_home')!r}")

    if args.fix:  # hand-made corrections from the map file win over the page
        perf_by_id = {p["id"]: p for ps in db_perfs.values() for p in ps}
        by_event = {f[0]: f for f in fixes}
        for eid, want in manual["event_fixes"].items():
            if only and eid not in only:
                continue
            db = db_events.get(eid)
            if not db:
                problems.append(f"{eid}: события нет в базе (раздел event_fixes в {os.path.basename(MAP_FILE)})")
                continue
            f = by_event.get(eid)
            if not f:
                f = by_event[eid] = (eid, {}, [], [])
                fixes.append(f)
            for k, v in want.items():
                if db.get(k) != v:
                    f[1][k] = v
                    if k == "day_evening":
                        f[3][:] = [n for n in f[3] if not n.startswith("day_evening")]
                        f[3].append(f"day_evening {db.get(k)!r} → {v!r}")
                else:
                    f[1].pop(k, None)
        for pid, want in manual["perfs"].items():
            if only and pid.split("_", 1)[0] not in only:
                continue
            p = perf_by_id.get(pid)
            if not p:
                problems.append(f"{pid}: исполнения нет в базе (раздел perfs в {os.path.basename(MAP_FILE)})")
                continue
            eid = p["events_id"]
            f = by_event.get(eid)
            if not f:
                f = by_event[eid] = (eid, {}, [], [])
                fixes.append(f)
            pp = next((x for x in f[2] if x["id"] == pid), None)
            if pp is None:
                pp = {"id": pid}
                f[2].append(pp)
            for k, v in want.items():
                if k in hidden:  # cannot be compared without the admin token: written only with --apply
                    if args.apply:
                        pp[k] = v
                elif p.get(k) != v:
                    pp[k] = v
                else:
                    pp.pop(k, None)
            if len(pp) == 1:
                f[2].remove(pp)

    legacy_ids = {i["event"]["id"] for i in legacy if "event" in i}
    for eid, e in sorted(db_events.items()) if not only else []:
        if eid not in legacy_ids and eid not in manual["db_only"] and eid.startswith(("L", "2")):
            diffs.append(f"{eid}: есть в базе, нет на старой странице ({e.get('date')}, {e.get('town')}, {e.get('place')})")

    # ─── report ──────────────────────────────────────────────────────────────
    print(f"Старая страница: {len(legacy)} концертов с {args.since} года; в базе событий: {len(db_events)}"
          + ("" if admin else " (публичный токен: черновики не видны)"))
    if args.fix:
        fixes = [f for f in fixes if f[1] or f[2] or f[3]]
        n_ev = sum(1 for f in fixes if f[1])
        n_perf = sum(len(f[2]) for f in fixes)
        print(f"\n== Исправить: событий {n_ev}, исполнений {n_perf}")
        for eid, patch, perf_patches, notes in fixes:
            parts = [f"{k} → {v!r}" for k, v in patch.items() if k != "day_evening"] + notes
            counts = {}
            for pp in perf_patches:
                for k, v in pp.items():
                    if k != "id":
                        counts[f"{k} → {v!r}"] = counts.get(f"{k} → {v!r}", 0) + 1
            parts += [f"песни: {k} ×{n}" for k, n in counts.items()]
            print(f"  {eid:15} " + "; ".join(parts))
        if not args.apply:
            print("\nНичего не записано. Запись: DIRECTUS_ADMIN_TOKEN=... scripts/legacy-concerts-sync.py --fix --apply")
            return
        for eid, patch, _, _ in fixes:
            if patch:
                api(f"/items/events/{urllib.parse.quote(eid)}", admin, "PATCH", patch)
        all_perfs = [pp for f in fixes for pp in f[2]]
        for i in range(0, len(all_perfs), 100):
            api("/items/perfs", admin, "PATCH", all_perfs[i:i + 100])
        print(f"исправлено событий: {n_ev}, исполнений: {n_perf}")
        return
    if delete_perfs:
        print(f"\n== Удалить исполнения (delete_perfs в {os.path.basename(MAP_FILE)}): {len(delete_perfs)}")
        by = {}
        for pid in delete_perfs:
            by.setdefault(pid.split("_", 1)[0], []).append(pid)
        for e, ids in by.items():
            print(f"  {e:15} {len(ids)}")
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
    existing_targets = [e for e in by_ev if e in db_events and e not in added_to]
    if renumber:
        print(f"\n== Перенумеровать исполнения (complete без места для вставки; reorder: "
              f"{', '.join(reordered) or 'нет'}): {len(renumber)}")
    if added_to:
        print(f"\n== Добавить в программы повторы, «???» и недостающее (complete): {sum(len(by_ev[e]) for e in added_to)}")
        for e in added_to:
            print(f"  {e:15} " + ", ".join(f"{p['id'].split('_', 1)[1]} (№ {p['num']})" for p in by_ev[e]))
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
    for i in range(0, len(delete_perfs), 100):
        api("/items/perfs", admin, "DELETE", delete_perfs[i:i + 100])
    if delete_perfs:
        print(f"удалено исполнений: {len(delete_perfs)}")
    for ev, _ in create_events:
        api("/items/events", admin, "POST", {k: v for k, v in ev.items() if v is not None})
        print("создано событие", ev["id"])
    for i in range(0, len(renumber), 100):
        api("/items/perfs", admin, "PATCH", renumber[i:i + 100])
    for i in range(0, len(create_perfs), 100):
        api("/items/perfs", admin, "POST", create_perfs[i:i + 100])
    print(f"создано исполнений: {len(create_perfs)}")


if __name__ == "__main__":
    main()
