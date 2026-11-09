#!/usr/bin/env python3
"""Проверка связей между каноном, шаблонами и схемами Angainor.

1. Каждая ссылка на templates/… или schemas/… из docs/canon/*.md ведёт на существующий файл.
2. Каждый файл в templates/ и schemas/ в первых строках объявляет правила: `canon: CODE, CODE`.
3. Каждый объявленный код существует в каноне.
4. Если правило ссылается на файл, файл объявляет это правило (связь в обе стороны).
5. Подробные файлы (docs/canon/NN-область/*.md) ссылаются только на существующие коды правил.
6. Относительные ссылки в docs/canon и docs/adr ведут на существующие файлы.

    python scripts/check_canon_links.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANON = ROOT / "docs" / "canon"
TARGETS = ("templates", "schemas")
HEAD_LINES = 6

RULE_RE = re.compile(r"^\*\*([A-Z]+-\d+)\.")
LINK_RE = re.compile(r"\]\(\.\./\.\./((?:templates|schemas)/[^)\s]+)\)")
DECL_RE = re.compile(r"canon:\s*([A-Z]+-\d+(?:\s*,\s*[A-Z]+-\d+)*)")
DETAIL_CODES_RE = re.compile(r"\[([A-Z]+-\d+)\]")
MD_LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
DOC_DIRS = ("docs/canon", "docs/adr")


def broken_links() -> list[str]:
    """Относительные ссылки в документации, которые никуда не ведут."""
    problems: list[str] = []
    for base in DOC_DIRS:
        for md in sorted((ROOT / base).rglob("*.md")):
            for target in MD_LINK_RE.findall(md.read_text(encoding="utf-8")):
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                path = target.split("#", 1)[0]
                if path and not (md.parent / path).exists():
                    problems.append(f"{md.relative_to(ROOT).as_posix()}: битая ссылка {target}")
    return problems


def detail_codes() -> dict[str, set[str]]:
    """Коды правил, на которые ссылаются подробные файлы в папках областей."""
    found: dict[str, set[str]] = {}
    for md in sorted(CANON.glob("*/*.md")):
        for line in md.read_text(encoding="utf-8").splitlines():
            if line.startswith("**Правила:**"):
                found[md.relative_to(ROOT).as_posix()] = set(DETAIL_CODES_RE.findall(line))
    return found


def canon_rules() -> tuple[set[str], dict[str, set[str]]]:
    """Коды правил и ссылки «правило → файл»."""
    codes: set[str] = set()
    links: dict[str, set[str]] = {}
    for md in sorted(CANON.glob("*.md")):
        current: str | None = None
        for line in md.read_text(encoding="utf-8").splitlines():
            if match := RULE_RE.match(line):
                current = match.group(1)
                codes.add(current)
            if current and line.startswith("↳"):
                for target in LINK_RE.findall(line):
                    links.setdefault(target, set()).add(current)
    return codes, links


def declared(path: Path) -> set[str]:
    head = path.read_text(encoding="utf-8").splitlines()[:HEAD_LINES]
    found: set[str] = set()
    for line in head:
        for match in DECL_RE.finditer(line):
            found |= {code.strip() for code in match.group(1).split(",")}
    return found


def main() -> int:
    codes, links = canon_rules()
    errors: list[str] = []

    for target, rules in sorted(links.items()):
        path = ROOT / target
        if not path.is_file():
            errors.append(f"{', '.join(sorted(rules))}: ссылка на несуществующий файл {target}")
            continue
        missing = rules - declared(path)
        if missing:
            errors.append(f"{target}: правило ссылается на файл, но файл не объявляет {', '.join(sorted(missing))}")

    for base in TARGETS:
        for path in sorted((ROOT / base).rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(ROOT).as_posix()
            codes_here = declared(path)
            if not codes_here:
                errors.append(f"{rel}: нет строки 'canon: CODE' в первых {HEAD_LINES} строках")
            for code in sorted(codes_here - codes):
                errors.append(f"{rel}: объявлено несуществующее правило {code}")

    for rel, used in detail_codes().items():
        for code in sorted(used - codes):
            errors.append(f"{rel}: ссылка на несуществующее правило {code}")
    errors += broken_links()

    if errors:
        print("Связи канона нарушены:", file=sys.stderr)
        for err in errors:
            print(f"  {err}", file=sys.stderr)
        return 1
    print(f"Связи канона в порядке: {len(codes)} правил, {len(links)} файлов со ссылками")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
