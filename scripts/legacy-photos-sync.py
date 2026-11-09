#!/usr/bin/env python3
"""Copy concert photos from the legacy concert list into static/photos/<event id>/.

The legacy page (LEGACY_URL) is still maintained, so the script is meant to be
run again and again; it only ADDS. A photo is taken only for an event whose
folder static/photos/<event id>/ does not exist yet: a folder that is already
there (a moved photo, a bigger one put in its place, several photos) is never
touched. See docs/photos-plan.md.

Legacy photos are conphoto/YYYYMMDD.jpg (YYYYMMDD_1 / _2 for the afternoon and
evening concerts of one day), 324×432, saved at JPEG quality 99. The name gives
the event id: 20240421_1.jpg -> L2024-04-21-1. Each photo is re-encoded at
quality 82 (≈35 KB instead of ≈120; kept as is if that is not smaller) and saved
as static/photos/<event id>/01.jpg.

Names that give no event in the database are listed. Map them by hand in
scripts/legacy-photos-sync.json (kept between runs):
    "photos": {"<legacy file name>": "<event id>"}
    "skip":   ["<legacy file name>", ...]          never copy, not reported

Usage:
    scripts/legacy-photos-sync.py                  # report only
    scripts/legacy-photos-sync.py --apply          # download and write files
    scripts/legacy-photos-sync.py --file page.html # local copy of the page
Needs ImageMagick (`magick`) for --apply. Reading uses the public Directus token,
so photos of draft events are listed as unmatched.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request

BASE = os.environ.get("DIRECTUS_URL", "https://db.sch.com.ru")
LEGACY_URL = "https://lambda.mkshch.com/fans/utf/concerts.html"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHOTOS = os.path.join(ROOT, "static", "photos")
MAP_FILE = os.path.join(ROOT, "scripts", "legacy-photos-sync.json")
UA = "schugo-legacy-photos-sync"
QUALITY = "82"
NAME = re.compile(r"^(\d{4})(\d\d)(\d\d)(?:_([12]))?\.jpg$")


def http_get(url, token=None):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def public_token():
    with open(os.path.join(ROOT, "config/_default/params.json.example")) as f:
        t = json.load(f)["directus"]["token"]
    return t.split("access_token=", 1)[-1]


def event_ids():
    q = urllib.parse.urlencode({"fields": "id", "limit": "-1"})
    data = json.loads(http_get(f"{BASE}/items/events?{q}", public_token()))["data"]
    return {e["id"] for e in data}


def id_from_name(name):
    m = NAME.match(name)
    if not m:
        return None
    y, mo, d, part = m.groups()
    return f"L{y}-{mo}-{d}" + (f"-{part}" if part else "")


def recompress(raw):
    """JPEG bytes at QUALITY, or the original bytes if that is not smaller."""
    with tempfile.TemporaryDirectory() as tmp:
        src, dst = os.path.join(tmp, "in.jpg"), os.path.join(tmp, "out.jpg")
        with open(src, "wb") as f:
            f.write(raw)
        subprocess.run(["magick", src, "-quality", QUALITY, dst], check=True)
        with open(dst, "rb") as f:
            out = f.read()
    return out if len(out) < len(raw) else raw


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--apply", action="store_true", help="download and write the photos")
    ap.add_argument("--file", help="local copy of the legacy page instead of downloading it")
    args = ap.parse_args()

    manual = {"photos": {}, "skip": []}
    if os.path.exists(MAP_FILE):
        with open(MAP_FILE) as f:
            manual.update(json.load(f))

    page = open(args.file, encoding="utf-8").read() if args.file else http_get(LEGACY_URL).decode("utf-8")
    names = list(dict.fromkeys(re.findall(r'src="conphoto/([^"]+)"', page)))
    ids = event_ids()

    todo, present, unmatched, taken = [], [], [], {}
    for name in names:
        if name in manual["skip"]:
            continue
        eid = manual["photos"].get(name) or id_from_name(name)
        if eid not in ids:
            unmatched.append(f"{name}" + (f" → {eid}: такого события в базе нет" if eid else ": имя не разобрано"))
            continue
        if eid in taken:
            unmatched.append(f"{name} → {eid}: уже занято снимком {taken[eid]}")
            continue
        taken[eid] = name
        (present if os.path.isdir(os.path.join(PHOTOS, eid)) else todo).append((name, eid))

    print(f"Снимков на старой странице: {len(names)}; уже есть в static/photos: {len(present)}")
    print(f"\n== Перенести: {len(todo)}")
    for name, eid in todo:
        print(f"  {name:16} → photos/{eid}/01.jpg")
    print(f"\n== Не сопоставлено: {len(unmatched)} (задать в {os.path.basename(MAP_FILE)})")
    for line in unmatched:
        print("  " + line)

    if not args.apply:
        print("\nНичего не записано. Запись: scripts/legacy-photos-sync.py --apply")
        return
    before = after = 0
    for name, eid in todo:
        raw = http_get(urllib.parse.urljoin(LEGACY_URL, "conphoto/" + name))
        out = recompress(raw)
        os.makedirs(os.path.join(PHOTOS, eid), exist_ok=True)
        with open(os.path.join(PHOTOS, eid, "01.jpg"), "wb") as f:
            f.write(out)
        before, after = before + len(raw), after + len(out)
    print(f"\nЗаписано снимков: {len(todo)}; {before // 1024} КБ → {after // 1024} КБ")


if __name__ == "__main__":
    sys.exit(main())
