#!/usr/bin/env python3
"""Проверка сообщений коммитов по Conventional Commits (канон CI-8, правило реестра CI-8).

Режимы:
    python scripts/check_commit_msg.py .git/COMMIT_EDITMSG     # хук commit-msg
    python scripts/check_commit_msg.py --message "feat: ..."   # одно сообщение
    python scripts/check_commit_msg.py --range origin/main..HEAD   # CI: все коммиты PR

Заголовок: `тип(область)?!?: описание`, не длиннее 100 символов.
Пропускаются служебные: Merge ..., Revert "...", fixup!/squash!/amend!.
Код возврата 1, если есть нарушения.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

TYPES = ("feat", "fix", "docs", "style", "refactor", "perf", "test", "build", "ci", "chore", "revert")
HEADER_RE = re.compile(r"^(" + "|".join(TYPES) + r")(\([^()\s]+\))?!?: \S.*$")
MAX_HEADER = 100
SKIP_RE = re.compile(r"^(Merge |Revert \"|fixup! |squash! |amend! )")


def check_message(message: str) -> list[str]:
    """Вернуть список нарушений для одного сообщения (пустой — всё в порядке)."""
    lines = [ln for ln in message.splitlines() if not ln.startswith("#")]
    header = next((ln for ln in lines if ln.strip()), "")
    if SKIP_RE.match(header):
        return []
    if not header:
        return ["пустое сообщение коммита"]
    errors: list[str] = []
    if not HEADER_RE.match(header):
        errors.append(f"заголовок не соответствует `тип(область): описание` (типы: {', '.join(TYPES)}): {header!r}")
    if len(header) > MAX_HEADER:
        errors.append(f"заголовок длиннее {MAX_HEADER} символов ({len(header)})")
    return errors


def commits_in_range(rev_range: str) -> list[tuple[str, str]]:
    out = subprocess.run(
        ["git", "log", "--format=%H%x1f%B%x1e", rev_range],
        capture_output=True, text=True, check=True, encoding="utf-8",
    ).stdout
    result = []
    for chunk in out.split("\x1e"):
        chunk = chunk.strip("\n")
        if chunk:
            sha, _, body = chunk.partition("\x1f")
            result.append((sha.strip()[:10], body))
    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", nargs="?", help="файл с сообщением (хук commit-msg)")
    ap.add_argument("--message", help="проверить переданное сообщение")
    ap.add_argument("--range", dest="rev_range", help="диапазон ревизий, например origin/main..HEAD")
    args = ap.parse_args(argv)

    if args.message is None and not args.file and not args.rev_range:
        ap.error("нужен файл, --message или --range")

    problems: list[str] = []
    if args.message is not None:
        problems += check_message(args.message)
    if args.file:
        problems += check_message(Path(args.file).read_text(encoding="utf-8"))
    if args.rev_range:
        for sha, body in commits_in_range(args.rev_range):
            problems += [f"{sha}: {e}" for e in check_message(body)]

    for p in problems:
        print(f"CI-8: {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
