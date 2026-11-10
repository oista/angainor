#!/usr/bin/env python3
"""Проверка реестра правил Angainor (ADR-0003).

1. Шапки правил и профилей проходят схемы (rule.schema.json, project-profile.schema.json).
2. Идентификаторы уникальны; имя файла, scope и расположение согласованы.
3. У каждого правила непустой раздел «Для агента».
4. `norm` ссылается на существующие коды канона.
5. supersedes / superseded_by ссылаются на существующие правила.
6. Профили: правила существуют, чужие проектные не подключены, выключение правила с norm требует waiver,
   режимы globs / on_request обеспечены globs / triggers.
7. Бюджет «всегда включённого» (в токенах) не превышен.
8. Фразы-триггеры не пересекаются у включённых правил одного проекта.
9. Закреплённая версия Angainor существует как git-тег (если теги есть).
10. enforce: инструмент из tools/ существует, matcher только у событий инструментов.
11. enforce: инструмент импортирует только стандартную библиотеку; ci требует stage и when.
12. С --repos-root: check проектных правил и waiver-ADR существуют в репозитории проекта.

    python scripts/check_rules.py [--repos-root PATH]
"""

from __future__ import annotations

import argparse
import ast
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_rules import render_core  # noqa: E402
from check_canon_links import RULE_RE  # noqa: E402
from rules_lib import ROOT, estimate_tokens, load_registry, resolve  # noqa: E402


def git_tags(root: Path) -> set[str] | None:
    try:
        out = subprocess.run(["git", "tag"], cwd=root, capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    return {t.strip() for t in out.splitlines() if t.strip()}


def tool_import_errors(root: Path, where: str, tool: str) -> list[str]:
    """Инструмент копируется в проект, поэтому может импортировать только стандартную библиотеку."""
    path = root / tool
    if not path.is_file():
        return []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError as exc:
        return [f"{where}: enforce: {tool} не разбирается: {exc.msg}"]
    bad = set()
    for node in ast.walk(tree):
        names = [a.name for a in node.names] if isinstance(node, ast.Import) else \
            [node.module or ""] if isinstance(node, ast.ImportFrom) and node.level == 0 else []
        bad |= {n.split(".")[0] for n in names if n and n.split(".")[0] not in sys.stdlib_module_names}
    return [f"{where}: enforce: {tool} импортирует не из стандартной библиотеки: {', '.join(sorted(bad))}"] if bad else []


def canon_codes_of(root: Path) -> set[str]:
    """Коды правил канона из root/docs/canon/*.md."""
    codes: set[str] = set()
    for md in sorted((root / "docs" / "canon").glob("*.md")):
        for line in md.read_text(encoding="utf-8").splitlines():
            if match := RULE_RE.match(line):
                codes.add(match.group(1))
    return codes


def waiver_exists(repo: Path, waiver: str) -> bool:
    num = "".join(ch for ch in waiver if ch.isdigit()).lstrip("0")
    adr_dir = repo / "docs" / "adr"
    if not adr_dir.is_dir():
        return False
    for f in adr_dir.glob("*.md"):
        digits = "".join(ch for ch in f.stem.split("-", 2)[1] if ch.isdigit()) if f.stem.upper().startswith("ADR-") else f.stem.split("-")[0]
        if digits.lstrip("0") == num:
            head = f.read_text(encoding="utf-8")[:1500]
            return "Accepted" in head
    return False


def run(root: Path = ROOT, repos_root: Path | None = None) -> tuple[list[str], list[str]]:
    reg = load_registry(root)
    errors = list(reg.errors)
    warnings = list(reg.warnings)

    canon_codes = canon_codes_of(root)
    for r in reg.rules.values():
        for code in r.norm:
            if canon_codes and code not in canon_codes:
                errors.append(f"{r.path}: norm ссылается на несуществующее правило канона {code}")
        for ref in r.supersedes + r.superseded_by:
            if ref not in reg.rules:
                errors.append(f"{r.path}: ссылка на несуществующее правило {ref}")

    tags = git_tags(root)
    used: set[str] = set()
    for project, prof in reg.profiles.items():
        eff, errs = resolve(reg, project)
        errors += errs
        used |= {e.rule.id for e in eff}

        core = render_core(eff, prof["angainor"]["version"], project)
        tokens = estimate_tokens(core) if any(e.enabled and e.activation == "always" for e in eff) else 0
        if tokens > prof["always_on_budget_tokens"]:
            errors.append(f"rules/projects/{project}/project.yaml: always-on ≈{tokens} токенов, бюджет {prof['always_on_budget_tokens']}")

        seen: dict[str, str] = {}
        for e in eff:
            if e.enabled and e.activation == "on_request":
                for t in e.rule.triggers:
                    key = t.strip().lower()
                    if key in seen and seen[key] != e.rule.id:
                        errors.append(f"проект {project}: фраза «{t}» у правил {seen[key]} и {e.rule.id}")
                    seen[key] = e.rule.id

        version = prof["angainor"]["version"]
        if tags:
            if version not in tags and f"v{version.lstrip('v')}" not in tags:
                errors.append(f"проект {project}: тег Angainor {version} не найден")
        else:
            warnings.append(f"проект {project}: в репозитории нет тегов, версия {version} не проверена")

        if repos_root:
            repo = repos_root / prof["repo"]
            if not repo.is_dir():
                warnings.append(f"проект {project}: репозиторий {repo} не найден, проверка check/waiver пропущена")
            else:
                for e in eff:
                    chk = e.rule.check
                    if chk and e.rule.scope == f"project:{project}" and not chk.startswith("angainor:") and not (repo / chk).exists():
                        errors.append(f"{e.rule.path}: check '{chk}' не найден в {repo}")
                    if e.waiver and not waiver_exists(repo, e.waiver):
                        errors.append(f"проект {project}: waiver {e.waiver} для {e.rule.id} не найден среди Accepted ADR")

    for rid, r in reg.rules.items():
        if rid not in used and r.status in ("Accepted", "Proposed"):
            warnings.append(f"{r.path}: правило не подключено ни к одному проекту")
        if r.check is None and r.status == "Accepted":
            warnings.append(f"{r.path}: нет check — правило остаётся пожеланием")
        for item in r.enforce:
            if not (root / item["tool"]).is_file():
                errors.append(f"{r.path}: enforce: инструмент '{item['tool']}' не найден в angainor")
            errors += tool_import_errors(root, r.path, item["tool"])
            if item["event"] == "ci" and not (item.get("stage") and item.get("when")):
                errors.append(f"{r.path}: enforce: для event=ci нужны stage и when")
            if item["event"] != "ci" and (item.get("stage") or item.get("when")):
                errors.append(f"{r.path}: enforce: stage и when допустимы только для event=ci")
            if item["event"] not in ("preToolUse", "postToolUse", "postToolUseFailure") and item.get("matcher"):
                errors.append(f"{r.path}: enforce: matcher допустим только для событий инструментов, не для {item['event']}")
        if r.enforce and not r.check:
            warnings.append(f"{r.path}: есть enforce, но не указан check")
        if r.check and r.check.startswith("angainor:") and not (root / r.check.split(":", 1)[1]).exists():
            errors.append(f"{r.path}: check '{r.check}' не найден в angainor")
    return errors, warnings


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repos-root", type=Path)
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--quiet", action="store_true", help="не печатать предупреждения")
    args = ap.parse_args(argv)
    errors, warnings = run(args.root, args.repos_root)
    if not args.quiet:
        for w in warnings:
            print(f"предупреждение: {w}")
    if errors:
        print("Реестр правил нарушен:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1
    reg = load_registry(args.root)
    print(f"Реестр правил в порядке: {len(reg.rules)} правил, {len(reg.profiles)} проектов")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
