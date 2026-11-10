#!/usr/bin/env python3
"""Защита проверок от ослабления (правило AGT-9, нормы QLT-6, TST-2).

Смотрит diff PR и ищет изменения, которыми легко «позеленить» CI вместо исправления причины:
  * правки конфигов проверок (workflows, pre-commit, ruff/mypy/pytest/coverage, Sonar, import-linter,
    хуки, копии инструментов Angainor);
  * добавленные `noqa`, `type: ignore`, `pragma: no cover`, `nosec`, `skip`/`xfail`, `continue-on-error`, `|| true`;
  * удалённые тесты;
  * сниженные пороги (fail_under, min_coverage) и повышенные лимиты (max_complexity, timeout…).

Находки блокируют PR, пока хотя бы в одном коммите диапазона нет строки `Checks-Change: <причина>`.
Причины печатаются в сводке: человек видит, что проверки меняли и зачем.

    python check_change_guard.py --range origin/main..HEAD
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import re
import subprocess
import sys

TRAILER_RE = re.compile(r"^Checks-Change:[ \t]*(\S.*?)[ \t]*$", re.M)
PROTECTED = (
    ".github/workflows/*", ".pre-commit-config.yaml", ".githooks/*", ".angainor/*",
    "ruff.toml", ".ruff.toml", "mypy.ini", ".coveragerc", "pytest.ini", "tox.ini", "setup.cfg",
    "sonar-project.properties", ".importlinter", "importlinter.ini",
)
PYPROJECT_KEYS = re.compile(r"fail[_-]under|ignore|select|exclude|omit|strict|disallow|timeout|addopts|testpaths|max[_-]")
MARKERS = (
    ("noqa", re.compile(r"#\s*noqa")),
    ("type: ignore", re.compile(r"#\s*type:\s*ignore")),
    ("pragma: no cover", re.compile(r"#\s*pragma:\s*no\s*cover")),
    ("nosec", re.compile(r"#\s*nosec")),
    ("pylint: disable", re.compile(r"#\s*pylint:\s*disable")),
    ("skip/xfail теста", re.compile(r"pytest\.mark\.(skip|skipif|xfail)|pytest\.(skip|xfail)\(|unittest\.skip")),
    ("--no-verify", re.compile(r"--no-verify")),
    ("continue-on-error", re.compile(r"continue-on-error:\s*true")),
    ("|| true", re.compile(r"\|\|\s*true\b")),
)
MARKER_SKIP = (".angainor/tools/*", ".cursor/*", "*.md", "*.mdc")
THRESHOLD_RE = re.compile(
    r"(?P<k>fail[_-]under|min[_-]coverage|max[_-]complexity|max[_-]line[_-]length|max[_-]args|timeout)"
    r"\s*[=:]?\s*[\"']?(?P<v>\d+(?:\.\d+)?)")
LOWER_IS_WEAKER = {"fail_under", "min_coverage"}
TEST_DEF_RE = re.compile(r"^\s*(?:async\s+)?def\s+test_")


def is_test_path(path: str) -> bool:
    name = path.rsplit("/", 1)[-1]
    return "/tests/" in f"/{path}" or name.startswith("test_") or name.endswith("_test.py")


def diff_range(rev_range: str) -> str:
    return rev_range if "..." in rev_range else rev_range.replace("..", "...", 1)


def read_diff(rev_range: str) -> dict[str, dict[str, list[str]]]:
    """Файл → {'added': [...], 'removed': [...]} по `git diff -U0`."""
    out = subprocess.run(["git", "diff", "-U0", "--no-color", "--no-ext-diff", diff_range(rev_range)],
                         capture_output=True, text=True, check=True, encoding="utf-8").stdout
    files: dict[str, dict[str, list[str]]] = {}
    current: str | None = None
    for line in out.splitlines():
        if line.startswith("diff --git "):
            current = line.split(" b/", 1)[-1]
            files.setdefault(current, {"added": [], "removed": []})
        elif line.startswith("+++ b/") or line.startswith("+++ "):
            if line[4:] != "/dev/null":
                current = line[6:] if line.startswith("+++ b/") else line[4:]
                files.setdefault(current, {"added": [], "removed": []})
        elif current and line.startswith("+") and not line.startswith("+++"):
            files[current]["added"].append(line[1:])
        elif current and line.startswith("-") and not line.startswith("---"):
            files[current]["removed"].append(line[1:])
    return files


def reasons_in(rev_range: str) -> list[str]:
    log = subprocess.run(["git", "log", "--format=%B%x1e", rev_range], capture_output=True, text=True,
                         check=True, encoding="utf-8").stdout
    return TRAILER_RE.findall(log)


def thresholds(lines: list[str]) -> dict[str, list[float]]:
    found: dict[str, list[float]] = {}
    for line in lines:
        for m in THRESHOLD_RE.finditer(line):
            found.setdefault(m.group("k").replace("-", "_"), []).append(float(m.group("v")))
    return found


def analyze(files: dict[str, dict[str, list[str]]]) -> list[str]:
    findings: list[str] = []
    for path, ch in sorted(files.items()):
        changed = ch["added"] + ch["removed"]
        if any(fnmatch.fnmatch(path, p) for p in PROTECTED) or \
                (path.endswith("pyproject.toml") and any(PYPROJECT_KEYS.search(x) for x in changed)):
            findings.append(f"{path}: изменён файл настроек проверок")
        if not any(fnmatch.fnmatch(path, p) for p in MARKER_SKIP):
            for name, rx in MARKERS:
                n = sum(1 for x in ch["added"] if rx.search(x))
                if n:
                    findings.append(f"{path}: добавлено «{name}» — {n}")
        if is_test_path(path):
            gone = sum(1 for x in ch["removed"] if TEST_DEF_RE.match(x)) - sum(1 for x in ch["added"] if TEST_DEF_RE.match(x))
            if gone > 0:
                findings.append(f"{path}: удалено тестов — {gone}")
        old, new = thresholds(ch["removed"]), thresholds(ch["added"])
        for key in sorted(set(old) & set(new)):
            weaker = min(new[key]) < max(old[key]) if key in LOWER_IS_WEAKER else max(new[key]) > min(old[key])
            if weaker:
                findings.append(f"{path}: порог {key} ослаблен ({old[key][0]:g} → {new[key][0]:g})")
    return findings


def write_summary(findings: list[str], reasons: list[str]) -> None:
    target = os.environ.get("GITHUB_STEP_SUMMARY")
    if not target:
        return
    lines = ["## Изменения проверок (AGT-9)", ""]
    if not findings:
        lines.append("Проверки не ослаблялись.")
    else:
        lines += [f"- {f}" for f in findings] + [""]
        lines.append("Причины (`Checks-Change`): " + ("; ".join(reasons) if reasons else "**не указаны — PR заблокирован**"))
    with open(target, "a", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--range", dest="rev_range", required=True, help="например origin/main..HEAD")
    args = ap.parse_args(argv)
    findings = analyze(read_diff(args.rev_range))
    reasons = reasons_in(args.rev_range) if findings else []
    write_summary(findings, reasons)
    for f in findings:
        print(f"AGT-9: {f}", file=sys.stderr)
    if findings and not reasons:
        print("AGT-9: проверки менялись без явной причины. Добавьте в коммит строку `Checks-Change: <причина>`.",
              file=sys.stderr)
        return 1
    if findings:
        print(f"AGT-9: изменения подтверждены ({'; '.join(reasons)})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
