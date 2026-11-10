#!/usr/bin/env python3
"""Размер PR (правило AGT-10, норма CI-5): PR маленькие и про одно.

Считает изменённые строки и файлы диапазона без lock-файлов и сгенерированного. Выше порога PR блокируется,
пока в одном из коммитов нет строки `Large-Change: <причина>`.

    python check_pr_size.py --range origin/main..HEAD [--max-lines 1000] [--max-files 50]
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import re
import subprocess
import sys

TRAILER_RE = re.compile(r"^Large-Change:[ \t]*(\S.*?)[ \t]*$", re.M)
EXCLUDE = (
    "*.lock", "uv.lock", "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock", "*.min.js", "*.min.css",
    ".angainor/tools/*", ".cursor/rules/angainor-*", ".cursor/hooks/angainor/*", ".cursor/plans/*",
    "docs/dialogs/*", "rules/RULE-INDEX.md", "rules/RULE-MATRIX.md", "rules/projects/*/RULES.md",
)


def diff_range(rev_range: str) -> str:
    return rev_range if "..." in rev_range else rev_range.replace("..", "...", 1)


def measure(rev_range: str) -> tuple[int, int]:
    out = subprocess.run(["git", "diff", "--numstat", "--no-color", diff_range(rev_range)], capture_output=True,
                         text=True, check=True, encoding="utf-8").stdout
    lines = files = 0
    for row in out.splitlines():
        added, deleted, path = (row.split("\t", 2) + ["", "", ""])[:3]
        if not path or any(fnmatch.fnmatch(path, p) for p in EXCLUDE) or not (added + deleted).replace("-", "").isdigit():
            continue
        files += 1
        lines += int(added) + int(deleted)
    return lines, files


def reasons_in(rev_range: str) -> list[str]:
    log = subprocess.run(["git", "log", "--format=%B%x1e", rev_range], capture_output=True, text=True, check=True,
                         encoding="utf-8").stdout
    return TRAILER_RE.findall(log)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--range", dest="rev_range", required=True)
    ap.add_argument("--max-lines", type=int, default=1000)
    ap.add_argument("--max-files", type=int, default=50)
    args = ap.parse_args(argv)
    lines, files = measure(args.rev_range)
    too_big = lines > args.max_lines or files > args.max_files
    reasons = reasons_in(args.rev_range) if too_big else []
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        verdict = "в норме" if not too_big else ("подтверждён: " + "; ".join(reasons) if reasons else "**слишком большой — PR заблокирован**")
        with open(summary, "a", encoding="utf-8") as fh:
            fh.write(f"## Размер PR (AGT-10)\n\n{lines} строк (лимит {args.max_lines}), {files} файлов (лимит {args.max_files}) — {verdict}\n")
    if too_big and not reasons:
        print(f"AGT-10: PR слишком большой: {lines} строк (лимит {args.max_lines}), {files} файлов (лимит {args.max_files}). "
              "Разбейте на серию PR или добавьте в коммит `Large-Change: <причина>`.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
