#!/usr/bin/env python3
"""Keep a local copy of the concert photos that the site build takes from Directus.

The build (layouts/miscellaneous/concerts.html, partial dx-photo.html) needs two copies of every
event photo, made by Directus presets: «concert-cover» for the first photo of an event and
«gallery» for every photo. Without this cache Hugo downloads all of them on every build.
This script fills assets/dx-photos/ with them:

    <file id>-<preset>-<version>.jpg

where version is the file's modified_on (or uploaded_on), digits only: a file replaced or edited
in Directus (a new focal point too) gets a new name and is downloaded again. A change of a preset
itself is not seen by the files: then bump PRESETS_VERSION here and in dx-photo.html.
Files no longer needed are removed, so the folder does not grow.

GitHub Actions keeps the folder between runs (actions/cache, see .github/workflows/static.yml).
Locally it is optional: without the folder the build downloads the photos itself.
The script never fails the build: on errors it only warns, and the template falls back to
downloading.

    scripts/photos-cache.py
"""
import json
import re
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "assets" / "dx-photos"
BASE = "https://db.sch.com.ru/"
PRESETS_VERSION = "1"  # то же значение — в layouts/partials/dx-photo.html


def token():
    p = ROOT / "config" / "_default" / "params.json"
    return json.loads(p.read_text(encoding="utf-8"))["directus"]["token"]


def fetch(url, tries=4):
    for k in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            # 503 «Under pressure»: Directus делает копии по пресету — подождать и повторить
            if e.code not in (429, 503) or k == tries - 1:
                raise
        except urllib.error.URLError:
            if k == tries - 1:
                raise
        time.sleep(5 * (k + 1))


def version(f):
    return PRESETS_VERSION + re.sub(r"\D", "", f.get("modified_on") or f.get("uploaded_on") or "")[:14]


def main():
    tok = token()
    url = (f"{BASE}items/events_files?limit=-1&fields=events_id,num,directus_files_id.id,"
           f"directus_files_id.modified_on,directus_files_id.uploaded_on{tok}")
    rows = json.loads(fetch(url))["data"]
    by_event = defaultdict(list)
    for r in rows:
        if r.get("directus_files_id"):
            by_event[r["events_id"]].append(r)
    want = {}
    for ps in by_event.values():
        ps.sort(key=lambda r: r["num"] or 0)
        for i, r in enumerate(ps):
            f = r["directus_files_id"]
            for preset in (["concert-cover", "gallery"] if i == 0 else ["gallery"]):
                want[f"{f['id']}-{preset}-{version(f)}.jpg"] = (f["id"], preset)

    DIR.mkdir(parents=True, exist_ok=True)
    have = {p.name for p in DIR.glob("*.jpg")}
    for name in have - set(want):
        (DIR / name).unlink()
    new = sorted(set(want) - have)

    def get(name):
        fid, preset = want[name]
        try:
            data = fetch(f"{BASE}assets/{fid}?key={preset}{tok}")
        except Exception as e:  # noqa: BLE001 — не валим сборку, шаблон скачает сам
            print(f"::warning::photos-cache: {fid} {preset}: {e}")
            return False
        (DIR / (name + ".part")).write_bytes(data)
        (DIR / (name + ".part")).rename(DIR / name)
        return True

    # несколько потоков, но немного: Directus при перегрузке отвечает 503 «Under pressure»
    with ThreadPoolExecutor(max_workers=6) as pool:
        errors = sum(1 for ok in pool.map(get, new) if not ok)
    print(f"photos-cache: {len(want)} needed, {len(want) - len(new)} cached, "
          f"{len(new) - errors} downloaded, {len(have - set(want))} removed, {errors} errors")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # noqa: BLE001
        print(f"::warning::photos-cache failed, the build downloads the photos itself: {e}")
    sys.exit(0)
