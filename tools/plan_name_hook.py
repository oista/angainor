#!/usr/bin/env python3
"""Хук Cursor для правила AGT-4: имя плана начинается с «Проект: ».

Читает JSON события из stdin, находит затронутые файлы `.cursor/plans/*.plan.md` и приводит
`name:` в шапке к виду «Проект: тема», а имя файла — к `проект_тема[_<8 hex>].plan.md`.
Всегда завершается с кодом 0 и печатает `{}` (fail-open): хук не должен ломать работу агента.

    python plan_name_hook.py --project clavis < event.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PATH_KEYS = ("file_path", "filePath", "path", "file", "path_relative")
NAME_RE = re.compile(r"^name:[ \t]*(.+?)[ \t]*$", re.M)
ID_RE = re.compile(r"_([0-9a-f]{8})\.plan\.md$")


def slug(text: str) -> str:
    return re.sub(r"_+", "_", re.sub(r"[^\w]+", "_", text.lower())).strip("_")


def candidates(data: dict) -> list[str]:
    out: list[str] = []
    for holder in (data, data.get("input"), data.get("tool_input"), data.get("result")):
        if isinstance(holder, dict):
            out += [str(holder[k]) for k in PATH_KEYS if holder.get(k)]
    return list(dict.fromkeys(out))


def roots_of(data: dict) -> list[str]:
    roots = list(data.get("workspace_roots") or data.get("workspaceRoots") or [])
    for k in ("cwd", "workspace_root", "workspaceRoot"):
        if data.get(k):
            roots.append(data[k])
    return [str(r) for r in roots]


def normalize(path: Path, project: str) -> Path | None:
    """Нормализует один файл плана. Возвращает новый путь, если файл переименован."""
    posix = path.as_posix()
    if not path.name.endswith(".plan.md") or "/.cursor/plans/" not in posix or not path.is_file():
        return None
    project_slug = slug(project)
    if not project_slug:
        return None

    raw = path.read_text(encoding="utf-8")
    match = NAME_RE.search(raw)
    name = match.group(1).strip("\"'") if match else path.name[: -len(".plan.md")]
    prefix = f"{project}:"
    new_name = name if name.lower().startswith(prefix.lower()) else f"{project}: {name}"

    id_match = ID_RE.search(path.name)
    plan_id = id_match.group(1) if id_match else None
    rest = path.name[: -len(".plan.md")]
    if plan_id:
        rest = rest[: -len(plan_id) - 1]
    new_base = path.name
    if not rest.startswith(project_slug + "_"):
        topic = slug(re.sub(r"^" + re.escape(project) + r"\s*:\s*", "", new_name, flags=re.I)) or rest
        new_base = f"{project_slug}_{topic}" + (f"_{plan_id}" if plan_id else "") + ".plan.md"

    new_raw = raw
    if new_name != name and match:
        new_raw = NAME_RE.sub(lambda _m: f"name: {new_name}", raw, count=1)
    if new_raw != raw:
        path.write_text(new_raw, encoding="utf-8", newline="")
    dest = path.with_name(new_base)
    if dest != path and not dest.exists():
        path.rename(dest)
        return dest
    return None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", required=True, help="префикс имени плана, например clavis или Isthmus")
    args = ap.parse_args(argv)
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
        roots = roots_of(data) if isinstance(data, dict) else []
        for cand in candidates(data) if isinstance(data, dict) else []:
            p = Path(cand)
            if not p.is_absolute() and roots:
                p = Path(roots[0]) / p
            normalize(p, args.project)
    except Exception:  # noqa: BLE001 — fail-open намеренно
        pass
    sys.stdout.write("{}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
