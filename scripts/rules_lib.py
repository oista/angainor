"""Общий код реестра правил Angainor (ADR-0003): загрузка, проверка схем, разрешение профилей.

Используется scripts/check_rules.py и scripts/build_rules.py. Нужны пакеты pyyaml и jsonschema.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
    from jsonschema import validators
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Нужны пакеты: pip install pyyaml jsonschema") from exc

ROOT = Path(__file__).resolve().parents[1]
FRONT_RE = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.S)
AGENT_RE = re.compile(r"^## Для агента[ \t]*\n(.*?)(?=^## |\Z)", re.S | re.M)
FILE_CODE_RE = re.compile(r"^([A-Z]{2,4}-[0-9]+)-.+\.md$")
MODES = ("always", "globs", "on_request")


@dataclass
class Rule:
    id: str
    title: str
    status: str
    scope: str
    activation: str
    globs: list[str] = field(default_factory=list)
    triggers: list[str] = field(default_factory=list)
    norm: list[str] = field(default_factory=list)
    check: str | None = None
    params: dict[str, Any] = field(default_factory=dict)
    supersedes: list[str] = field(default_factory=list)
    superseded_by: list[str] = field(default_factory=list)
    agent_text: str = ""
    path: str = ""


@dataclass
class Effective:
    rule: Rule
    enabled: bool
    activation: str
    globs: list[str]
    params: dict[str, Any]
    reason: str | None = None
    waiver: str | None = None


@dataclass
class Registry:
    root: Path
    rules: dict[str, Rule] = field(default_factory=dict)
    profiles: dict[str, dict[str, Any]] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def estimate_tokens(text: str) -> int:
    """Приближение: ~3 символа на токен (русский текст). Единый способ для всех проверок."""
    return math.ceil(len(text) / 3)


def _schema(root: Path, name: str) -> Any:
    schema = json.loads((root / "schemas" / name).read_text(encoding="utf-8"))
    cls = validators.validator_for(schema)
    cls.check_schema(schema)
    return cls(schema)


def _schema_errors(validator: Any, data: Any, where: str) -> list[str]:
    out = []
    for err in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
        loc = "/".join(str(p) for p in err.path) or "(корень)"
        out.append(f"{where}: {loc}: {err.message[:140]}")
    return out


def _rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def load_registry(root: Path = ROOT) -> Registry:
    reg = Registry(root=root)
    rule_v = _schema(root, "rule.schema.json")
    prof_v = _schema(root, "project-profile.schema.json")
    base = root / "rules"

    files: list[tuple[Path, str]] = []  # (файл, ожидаемый scope)
    for md in sorted((base / "shared").rglob("*.md")) if (base / "shared").is_dir() else []:
        files.append((md, "shared"))
    for md in sorted(base.glob("projects/*/rules/*.md")):
        files.append((md, f"project:{md.parents[1].name}"))

    for path, expected_scope in files:
        rel = _rel(root, path)
        text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        match = FRONT_RE.match(text)
        if not match:
            reg.errors.append(f"{rel}: нет YAML-шапки")
            continue
        try:
            header = yaml.safe_load(match.group(1))
        except yaml.YAMLError as exc:
            reg.errors.append(f"{rel}: YAML не читается: {str(exc)[:100]}")
            continue
        if not isinstance(header, dict):
            reg.errors.append(f"{rel}: шапка должна быть словарём")
            continue
        errs = _schema_errors(rule_v, header, rel)
        reg.errors += errs
        if errs:
            continue

        rid = header["id"]
        code_match = FILE_CODE_RE.match(path.name)
        if not code_match or code_match.group(1) != rid.split(".")[-1]:
            reg.errors.append(f"{rel}: имя файла должно начинаться с {rid.split('.')[-1]}-")
        if header["scope"] != expected_scope:
            reg.errors.append(f"{rel}: scope '{header['scope']}', ожидается '{expected_scope}' по расположению")
        if expected_scope.startswith("project:") and not rid.startswith(expected_scope.split(":", 1)[1] + "."):
            reg.errors.append(f"{rel}: идентификатор проектного правила должен начинаться с '{expected_scope.split(':', 1)[1]}.'")
        if rid in reg.rules:
            reg.errors.append(f"{rel}: идентификатор {rid} уже занят ({reg.rules[rid].path})")
            continue
        section = AGENT_RE.search(match.group(2))
        agent_text = section.group(1).strip() if section else ""
        if not agent_text:
            reg.errors.append(f"{rel}: нет непустого раздела «## Для агента»")

        reg.rules[rid] = Rule(
            id=rid, title=header["title"], status=header["status"], scope=header["scope"],
            activation=header["activation"], globs=header.get("globs") or [],
            triggers=header.get("triggers") or [], norm=header.get("norm") or [],
            check=header.get("check"), params=header.get("params") or {},
            supersedes=header.get("supersedes") or [], superseded_by=header.get("superseded_by") or [],
            agent_text=agent_text, path=rel,
        )

    for prof_path in sorted(base.glob("projects/*/project.yaml")):
        rel = _rel(root, prof_path)
        try:
            data = yaml.safe_load(prof_path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            reg.errors.append(f"{rel}: YAML не читается: {str(exc)[:100]}")
            continue
        if not isinstance(data, dict):
            reg.errors.append(f"{rel}: профиль должен быть словарём")
            continue
        errs = _schema_errors(prof_v, data, rel)
        reg.errors += errs
        if errs:
            continue
        if data["project"] != prof_path.parent.name:
            reg.errors.append(f"{rel}: project '{data['project']}' не совпадает с именем папки '{prof_path.parent.name}'")
            continue
        reg.profiles[data["project"]] = data
    return reg


def resolve(reg: Registry, project: str) -> tuple[list[Effective], list[str]]:
    """Эффективный набор правил проекта: правило + переопределения профиля."""
    profile = reg.profiles[project]
    out: list[Effective] = []
    errors: list[str] = []
    where = f"rules/projects/{project}/project.yaml"
    for rid, entry in profile["rules"].items():
        rule = reg.rules.get(rid)
        if rule is None:
            errors.append(f"{where}: правило {rid} не найдено в реестре")
            continue
        if rule.scope.startswith("project:") and rule.scope != f"project:{project}":
            errors.append(f"{where}: {rid} — правило другого проекта ({rule.scope})")
            continue
        e = {} if entry is True else entry
        enabled = e.get("enabled", True)
        activation = e.get("activation", rule.activation)
        globs = e.get("globs", rule.globs)
        params = {**rule.params, **e.get("params", {})}
        if enabled:
            if rule.status == "Superseded":
                errors.append(f"{where}: {rid} включено, но Superseded (заменено: {', '.join(rule.superseded_by) or '?'})")
            if activation == "globs" and not globs:
                errors.append(f"{where}: {rid}: режим globs требует непустой globs (в правиле или в профиле)")
            if activation == "on_request" and not rule.triggers:
                errors.append(f"{where}: {rid}: режим on_request требует triggers в правиле")
        else:
            if rule.norm and not e.get("waiver"):
                errors.append(f"{where}: {rid} выключено, но у правила есть norm ({', '.join(rule.norm)}): нужен waiver: ADR-…")
        out.append(Effective(rule, enabled, activation, globs, params, e.get("reason"), e.get("waiver")))
    return out, errors
