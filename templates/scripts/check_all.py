#!/usr/bin/env python3
# canon: CI-1, LAY-4
"""Единая точка запуска всех проверок — локально и в CI.

Источник: moex-data-model scripts/check_all.py. CI вызывает этот файл
по шагам (--only <шаг>) и не содержит своей логики проверок.

    python scripts/check_all.py               # всё подряд, стоп на первой ошибке
    python scripts/check_all.py --keep-going  # всё, итог в конце
    python scripts/check_all.py --only unit   # один шаг
    python scripts/check_all.py --list        # список шагов
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable

# Порядок — от быстрых проверок к медленным (CI-2). Имя шага — команда.
STEPS: list[tuple[str, list[str]]] = [
    ("encoding", [PY, "scripts/check_mojibake.py"]),
    ("lock", ["uv", "lock", "--check"]),
    ("config", [PY, "-m", "__pkg__.settings", "--check-env-example"]),
    ("ruff", ["ruff", "check", "src", "tests", "scripts"]),
    ("imports", ["lint-imports"]),
    ("mypy", ["mypy", "src"]),
    ("architecture", [PY, "-m", "pytest", "tests/architecture", "-q"]),
    ("unit", [PY, "-m", "pytest", "tests/unit", "-q", "--ignore=tests/unit/quarantine",
              "--timeout=45", "--durations=20"]),
    ("integration", [PY, "-m", "pytest", "tests/integration", "-q", "-m", "integration"]),
]


def run(name: str, cmd: list[str]) -> bool:
    print(f"\n=== {name}: {' '.join(cmd)}", flush=True)
    started = time.monotonic()
    code = subprocess.call(cmd, cwd=ROOT)
    status = "OK" if code == 0 else f"FAIL ({code})"
    print(f"=== {name}: {status} за {time.monotonic() - started:.1f} с", flush=True)
    return code == 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--only", action="append", help="запустить только указанные шаги")
    parser.add_argument("--keep-going", action="store_true", help="не останавливаться на ошибке")
    parser.add_argument("--list", action="store_true", help="показать шаги и выйти")
    args = parser.parse_args(argv)

    if args.list:
        for name, cmd in STEPS:
            print(f"{name:14} {' '.join(cmd)}")
        return 0

    selected = [s for s in STEPS if not args.only or s[0] in args.only]
    unknown = set(args.only or []) - {name for name, _ in STEPS}
    if unknown:
        print(f"Неизвестные шаги: {', '.join(sorted(unknown))}", file=sys.stderr)
        return 2

    failed: list[str] = []
    for name, cmd in selected:
        if not run(name, cmd):
            failed.append(name)
            if not args.keep_going:
                break
    if failed:
        print(f"\nУпали шаги: {', '.join(failed)}", file=sys.stderr)
        return 1
    print("\nВсе проверки пройдены")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
