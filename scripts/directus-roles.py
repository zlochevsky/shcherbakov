#!/usr/bin/env python3
"""Directus roles and policies by work area (see README, «Направления работы»).

Creates or updates, by name:
- the policy READ_POLICY: read access to all site tables, Studio access,
  editing one's own profile;
- one policy per area: create/read/update/delete in the area's tables;
- one role per area with both policies attached.

The script is idempotent: a policy's permissions are replaced with the ones
listed here on every run; roles and links are created only if missing.
Users are not touched: assign roles in Studio (User Directory).
The existing role «content editor» (all tables) is left as it is.

Usage (admin token only from the environment, never on the command line):
    DIRECTUS_ADMIN_TOKEN=... scripts/directus-roles.py            # dry run
    DIRECTUS_ADMIN_TOKEN=... scripts/directus-roles.py --apply
Afterwards refresh the export: scripts/directus-schema.py --fetch
"""
import json
import os
import sys
import urllib.parse
import urllib.request

BASE = os.environ.get("DIRECTUS_URL", "https://db.sch.com.ru")

SITE_TABLES = [
    "announces", "book_sets", "books", "books_entries", "comments", "cycles",
    "cycles_entries", "disk_formats", "events", "events_performers_3",
    "languages", "links", "log_entries", "performers", "performers_members",
    "perfs", "perfs_performers_1", "recordings", "recordings_performers",
    "releases", "releases_performers", "sets", "sets_entries", "statements",
    "statements_works", "translations", "translations_translators",
    "translators", "variants", "works", "works_see_also",
]

READ_POLICY = {
    "name": "Чтение всех таблиц (редакторы)",
    "icon": "visibility",
    "description": "чтение всех таблиц сайта, вход в Studio, правка своего профиля",
}

PROFILE_FIELDS = [
    "first_name", "last_name", "email", "password", "location", "title",
    "description", "tags", "avatar", "language", "appearance",
    "theme_light", "theme_dark",
]

# area -> (icon, tables with create/update/delete, tables with create/update only)
AREAS = {
    "События": ("event", ["announces", "log_entries"], ["events"]),
    "Фан-клуб, исполнители, критика": ("forum", [
        "links", "recordings", "recordings_performers", "releases",
        "releases_performers", "performers", "performers_members",
        "comments", "works_see_also"], []),
    "Исполнения": ("album", [
        "events", "events_performers_3", "perfs", "perfs_performers_1",
        "sets", "sets_entries", "disk_formats", "books", "book_sets",
        "books_entries"], []),
    "Тексты и музыкальная часть": ("lyrics", [
        "works", "variants", "cycles", "cycles_entries"], []),
    "Высказывания": ("format_quote", ["statements", "statements_works"], []),
    "Языковые разделы": ("translate", [
        "translations", "translations_translators", "translators",
        "languages", "links"], []),
}


def api(method, path, body=None, params=None):
    url = BASE + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": "Bearer " + TOKEN,
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req) as r:
            raw = r.read()
    except urllib.error.HTTPError as e:
        sys.exit(f"{method} {path}: {e.code} {e.read().decode()[:500]}")
    return json.loads(raw)["data"] if raw else None


def find(collection, name):
    rows = api("GET", f"/{collection}", params={
        "filter[name][_eq]": name, "fields": "id", "limit": 1})
    return rows[0]["id"] if rows else None


def ensure_policy(spec, perms):
    pid = find("policies", spec["name"])
    print(f"policy «{spec['name']}»: {'exists' if pid else 'create'}, "
          f"{len(perms)} permissions")
    if not APPLY:
        return pid or "(new)"
    if not pid:
        pid = api("POST", "/policies", {**spec, "admin_access": False,
                                        "app_access": True})["id"]
    old = api("GET", "/permissions", params={
        "filter[policy][_eq]": pid, "fields": "id", "limit": -1})
    if old:
        api("DELETE", "/permissions", [p["id"] for p in old])
    api("POST", "/permissions", [{**p, "policy": pid} for p in perms])
    return pid


def ensure_role(name, icon, policies):
    rid = find("roles", name)
    print(f"role «{name}»: {'exists' if rid else 'create'}")
    if not APPLY:
        return
    if not rid:
        rid = api("POST", "/roles", {"name": name, "icon": icon})["id"]
    for pid in policies:
        have = api("GET", "/access", params={
            "filter[role][_eq]": rid, "filter[policy][_eq]": pid,
            "fields": "id", "limit": 1})
        if not have:
            api("POST", "/access", {"role": rid, "policy": pid})


def perm(collection, action, **extra):
    return {"collection": collection, "action": action, "fields": ["*"],
            "permissions": {}, "validation": {}, **extra}


def main():
    read = [perm(t, "read") for t in SITE_TABLES]
    read.append(perm("directus_users", "update", fields=PROFILE_FIELDS,
                     permissions={"id": {"_eq": "$CURRENT_USER"}}))
    read_id = ensure_policy(READ_POLICY, read)

    for area, (icon, full, cu) in AREAS.items():
        perms = [perm(t, a) for t in full for a in ("create", "update", "delete")]
        perms += [perm(t, a) for t in cu for a in ("create", "update")]
        pid = ensure_policy({"name": f"Направление: {area}", "icon": icon,
                             "description": "создание, правка и удаление в таблицах направления"},
                            perms)
        ensure_role(f"Редактор: {area}", icon, [read_id, pid])

    if not APPLY:
        print("\ndry run; add --apply to write")


if __name__ == "__main__":
    TOKEN = os.environ.get("DIRECTUS_ADMIN_TOKEN") or sys.exit(
        "DIRECTUS_ADMIN_TOKEN is not set")
    APPLY = "--apply" in sys.argv[1:]
    main()
