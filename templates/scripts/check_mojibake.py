#!/usr/bin/env python3
# canon: QLT-4
"""Падает, если текстовый файл не в UTF-8 или содержит «кракозябры».

Источник: Clavis scripts/check_mojibake.py. Добавлено: проверка, что файл
читается как UTF-8 (ловит, например, workflow, сохранённый в UTF-16).
Шаблоны испорченного текста собираются из кодов символов, чтобы сами
документы и CI их не содержали.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Типичные обломки CP1251, прочитанного как UTF-8: тире, «не равно», многоточие, стрелка.
_PATTERNS = (
    chr(0x0432) + chr(0x0402),
    chr(0x0432) + chr(0x2030),
    chr(0x0432) + chr(0x2020),
)
_SUFFIXES = {".md", ".py", ".yaml", ".yml", ".toml", ".json", ".ttl", ".txt"}
_DEFAULT_ROOTS = ("docs", "src", "scripts", "tests", "config", ".github")
_SKIP_PARTS = (("docs", "archive"),)


def _skipped(path: Path, repo: Path) -> bool:
    parts = path.relative_to(repo).parts
    if any(parts[: len(skip)] == skip for skip in _SKIP_PARTS):
        return True
    return parts[-2:] == ("scripts", "check_mojibake.py")


def scan(repo: Path, roots: list[str]) -> list[str]:
    hits: list[str] = []
    for name in roots:
        base = repo / name
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in _SUFFIXES or _skipped(path, repo):
                continue
            rel = path.relative_to(repo)
            try:
                text = path.read_bytes().decode("utf-8")
            except UnicodeDecodeError:
                hits.append(f"{rel}: файл не в UTF-8")
                continue
            for i, line in enumerate(text.splitlines(), 1):
                if any(p in line for p in _PATTERNS):
                    hits.append(f"{rel}:{i}: испорченная кодировка")
    return hits


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    hits = scan(args.root.resolve(), list(_DEFAULT_ROOTS))
    if hits:
        print("\n".join(hits), file=sys.stderr)
        return 1
    print("Кодировка в порядке")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
