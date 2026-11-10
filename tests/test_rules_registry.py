"""Тесты реестра правил: scripts/check_rules.py и scripts/build_rules.py (ADR-0003)."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

REAL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REAL / "scripts"))

import build_rules  # noqa: E402
import check_rules  # noqa: E402

RULE = """---
id: {id}
title: {title}
status: Accepted
scope: {scope}
activation: {activation}
globs: {globs}
triggers: {triggers}
norm: {norm}
check: {check}
---

# {id}

## Для агента

{text}

## Зачем

тест
"""


def write_rule(root: Path, rel: str, **kw) -> None:
    d = dict(id="AGT-1", title="Порядок прав", scope="shared", activation="always", globs="[]",
             triggers="[]", norm="[]", check="null", text="Сначала Accepted ADR.")
    d.update(kw)
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(RULE.format(**d), encoding="utf-8")


def write_profile(root: Path, project: str, rules_yaml: str, budget: int = 900, repo: str | None = None) -> None:
    path = root / "rules" / "projects" / project / "project.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"project: {project}\nrepo: {repo or project}\nangainor: {{version: 0.1.0}}\n"
        f"always_on_budget_tokens: {budget}\nrules:\n{rules_yaml}", encoding="utf-8")


@pytest.fixture()
def root(tmp_path: Path) -> Path:
    shutil.copytree(REAL / "schemas", tmp_path / "schemas")
    (tmp_path / "docs" / "canon").mkdir(parents=True)
    return tmp_path


def errors(root: Path) -> list[str]:
    return check_rules.run(root)[0]


def test_empty_registry_is_ok(root):
    assert errors(root) == []


def test_valid_registry(root):
    write_rule(root, "rules/shared/agent/AGT-1-order.md")
    write_rule(root, "rules/shared/agent/AGT-6-ci.md", id="AGT-6", title="CI", activation="on_request",
               triggers="['проверь CI']", check="angainor:scripts/check_rules.py")
    (root / "scripts").mkdir()
    (root / "scripts" / "check_rules.py").write_text("", encoding="utf-8")
    write_profile(root, "demo", "  AGT-1: true\n  AGT-6: true\n")
    assert errors(root) == []


def test_duplicate_id(root):
    write_rule(root, "rules/shared/agent/AGT-1-a.md")
    write_rule(root, "rules/shared/docs/AGT-1-b.md")
    assert any("уже занят" in e for e in errors(root))


def test_filename_must_match_id(root):
    write_rule(root, "rules/shared/agent/AGT-2-wrong.md", id="AGT-1")
    assert any("имя файла" in e for e in errors(root))


def test_scope_must_match_location(root):
    write_rule(root, "rules/shared/agent/AGT-1-a.md", scope="project:demo", id="demo.AGT-1")
    assert any("scope" in e for e in errors(root))


def test_project_rule_prefix(root):
    write_rule(root, "rules/projects/demo/rules/DB-1-fk.md", id="other.DB-1", scope="project:demo")
    assert any("начинаться с 'demo.'" in e for e in errors(root))


def test_missing_agent_section(root):
    write_rule(root, "rules/shared/agent/AGT-1-a.md", text="")
    assert any("Для агента" in e for e in errors(root))


def test_unknown_norm(root):
    (root / "docs" / "canon" / "07.md").write_text("**DOC-3.** x\n", encoding="utf-8")
    write_rule(root, "rules/shared/agent/AGT-1-a.md", norm="[ZZ-9]")
    assert any("ZZ-9" in e for e in errors(root))


def test_unknown_rule_in_profile(root):
    write_profile(root, "demo", "  AGT-9: true\n")
    assert any("не найдено в реестре" in e for e in errors(root))


def test_other_project_rule_forbidden(root):
    write_rule(root, "rules/projects/a/rules/DB-1-fk.md", id="a.DB-1", scope="project:a")
    write_profile(root, "b", "  a.DB-1: true\n")
    assert any("правило другого проекта" in e for e in errors(root))


def test_disable_rule_with_norm_needs_waiver(root):
    write_rule(root, "rules/shared/agent/AGT-1-a.md", norm="[DOC-3]")
    (root / "docs" / "canon" / "07.md").write_text("**DOC-3.** x\n", encoding="utf-8")
    write_profile(root, "demo", "  AGT-1:\n    enabled: false\n    reason: нет\n")
    assert any("нужен waiver" in e for e in errors(root))


def test_disable_rule_with_norm_and_waiver_ok(root):
    write_rule(root, "rules/shared/agent/AGT-1-a.md", norm="[DOC-3]")
    (root / "docs" / "canon" / "07.md").write_text("**DOC-3.** x\n", encoding="utf-8")
    write_profile(root, "demo", "  AGT-1:\n    enabled: false\n    reason: нет\n    waiver: ADR-0044\n")
    assert errors(root) == []


def test_disable_without_norm_needs_only_reason(root):
    write_rule(root, "rules/shared/agent/AGT-1-a.md")
    write_profile(root, "demo", "  AGT-1:\n    enabled: false\n    reason: форматтер в pre-commit\n")
    assert errors(root) == []


def test_disable_without_reason_rejected_by_schema(root):
    write_rule(root, "rules/shared/agent/AGT-1-a.md")
    write_profile(root, "demo", "  AGT-1:\n    enabled: false\n")
    assert errors(root)


def test_globs_override_requires_globs(root):
    write_rule(root, "rules/shared/agent/AGT-1-a.md")
    write_profile(root, "demo", "  AGT-1: {activation: globs}\n")
    assert any("globs" in e for e in errors(root))


def test_on_request_override_requires_triggers(root):
    write_rule(root, "rules/shared/agent/AGT-1-a.md")
    write_profile(root, "demo", "  AGT-1: {activation: on_request}\n")
    assert any("triggers" in e for e in errors(root))


def test_budget_exceeded(root):
    write_rule(root, "rules/shared/agent/AGT-1-a.md", text="слово " * 400)
    write_profile(root, "demo", "  AGT-1: true\n", budget=100)
    assert any("бюджет" in e for e in errors(root))


def test_trigger_collision(root):
    write_rule(root, "rules/shared/agent/AGT-1-a.md", activation="on_request", triggers="['Зафиксируй']")
    write_rule(root, "rules/shared/agent/AGT-2-b.md", id="AGT-2", activation="on_request", triggers="['зафиксируй']")
    write_profile(root, "demo", "  AGT-1: true\n  AGT-2: true\n")
    assert any("фраза" in e for e in errors(root))


def test_superseded_cannot_be_enabled(root):
    write_rule(root, "rules/shared/agent/AGT-1-a.md")
    p = root / "rules/shared/agent/AGT-1-a.md"
    p.write_text(p.read_text(encoding="utf-8").replace("status: Accepted", "status: Superseded\nsuperseded_by: [AGT-2]"), encoding="utf-8")
    write_rule(root, "rules/shared/agent/AGT-2-b.md", id="AGT-2")
    write_profile(root, "demo", "  AGT-1: true\n")
    assert any("Superseded" in e for e in errors(root))


def test_check_path_in_repo(root, tmp_path_factory):
    repos = tmp_path_factory.mktemp("repos")
    (repos / "demo").mkdir()
    write_rule(root, "rules/projects/demo/rules/DB-1-fk.md", id="demo.DB-1", scope="project:demo", check="scripts/nope.py")
    write_profile(root, "demo", "  demo.DB-1: true\n")
    assert any("не найден" in e for e in check_rules.run(root, repos)[0])
    (repos / "demo" / "scripts").mkdir()
    (repos / "demo" / "scripts" / "nope.py").write_text("", encoding="utf-8")
    assert check_rules.run(root, repos)[0] == []


def test_waiver_adr_must_be_accepted(root, tmp_path_factory):
    repos = tmp_path_factory.mktemp("repos")
    adr = repos / "demo" / "docs" / "adr"
    adr.mkdir(parents=True)
    write_rule(root, "rules/shared/agent/AGT-1-a.md", norm="[DOC-3]")
    (root / "docs" / "canon" / "07.md").write_text("**DOC-3.** x\n", encoding="utf-8")
    write_profile(root, "demo", "  AGT-1:\n    enabled: false\n    reason: x\n    waiver: ADR-0044\n")
    assert any("waiver" in e for e in check_rules.run(root, repos)[0])
    (adr / "ADR-0044-x.md").write_text("**Статус:** Proposed\n", encoding="utf-8")
    assert any("waiver" in e for e in check_rules.run(root, repos)[0])
    (adr / "ADR-0044-x.md").write_text("**Статус:** Accepted\n", encoding="utf-8")
    assert check_rules.run(root, repos)[0] == []


# ---- сборка ----

def build_fixture(root: Path) -> Path:
    write_rule(root, "rules/shared/agent/AGT-1-order.md")
    write_rule(root, "rules/shared/docs/DOC-4-term.md", id="DOC-4", title="Термин", activation="globs", globs="['docs/**']",
               text="Новый термин — в глоссарий.")
    write_rule(root, "rules/shared/agent/AGT-6-ci.md", id="AGT-6", title="CI", activation="on_request", triggers="['проверь CI']",
               text="Смотри Actions.")
    write_profile(root, "demo", "  AGT-1: true\n  DOC-4: true\n  AGT-6: true\n", repo="demo")
    repos = root.parent / (root.name + "_repos")
    (repos / "demo").mkdir(parents=True)
    return repos


def test_build_writes_projections_and_is_idempotent(root):
    repos = build_fixture(root)
    assert build_rules.main(["--root", str(root), "--projections", "--repos-root", str(repos)]) == 0
    repo = repos / "demo"
    core = (repo / ".cursor/rules/angainor-core.mdc").read_text(encoding="utf-8")
    assert "alwaysApply: true" in core and "Сначала Accepted ADR." in core
    assert "globs: docs/**" in (repo / ".cursor/rules/angainor-DOC-4.mdc").read_text(encoding="utf-8")
    assert "«проверь CI»" in (repo / ".cursor/rules/angainor-AGT-6.mdc").read_text(encoding="utf-8")
    agents = (repo / "AGENTS.md").read_text(encoding="utf-8")
    assert build_rules.BEGIN in agents and "AGT-1" in agents
    assert build_rules.main(["--root", str(root), "--check", "--repos-root", str(repos)]) == 0


def test_check_detects_drift_and_keeps_handwritten_agents_text(root):
    repos = build_fixture(root)
    repo = repos / "demo"
    (repo / "AGENTS.md").write_text("# Агентам\n\nРукописный текст.\n", encoding="utf-8")
    build_rules.main(["--root", str(root), "--projections", "--repos-root", str(repos)])
    agents = (repo / "AGENTS.md").read_text(encoding="utf-8")
    assert "Рукописный текст." in agents
    (repo / ".cursor/rules/angainor-core.mdc").write_text("правлено руками", encoding="utf-8")
    assert build_rules.main(["--root", str(root), "--check", "--repos-root", str(repos)]) == 1


def test_disabled_rule_not_projected_and_stale_file_reported(root, capsys):
    repos = build_fixture(root)
    build_rules.main(["--root", str(root), "--projections", "--repos-root", str(repos)])
    write_profile(root, "demo", "  AGT-1: true\n  DOC-4:\n    enabled: false\n    reason: тест\n  AGT-6: true\n", repo="demo")
    assert build_rules.main(["--root", str(root), "--check", "--repos-root", str(repos)]) == 1
    assert "лишний сгенерированный файл" in capsys.readouterr().err


def test_registry_pages(root):
    build_fixture(root)
    build_rules.main(["--root", str(root)])
    index = (root / "rules/RULE-INDEX.md").read_text(encoding="utf-8")
    matrix = (root / "rules/RULE-MATRIX.md").read_text(encoding="utf-8")
    page = (root / "rules/projects/demo/RULES.md").read_text(encoding="utf-8")
    assert "AGT-6" in index and "пожелание" in index
    assert "| demo |" in matrix and "●" in matrix and "◐" in matrix and "○" in matrix
    assert "токенов из 900" in page


def test_fill_substitutes_and_drops_empty_lines():
    import rules_lib
    text = "Команда: {{cmd}}\n{{extra}}\nКонец"
    assert rules_lib.fill(text, {"cmd": "pytest", "extra": ""}) == "Команда: pytest\nКонец"
    assert rules_lib.fill("a {{x}}", {"x": ["1", "2"]}) == "a 1, 2"
    assert rules_lib.placeholders("{{a}} и {{ b }}") == {"a", "b"}


def test_params_are_projected_and_unresolved_is_error(root):
    write_rule(root, "rules/shared/agent/AGT-8-pr.md", id="AGT-8", title="PR",
               text="Проверка: {{check_command}}")
    write_profile(root, "demo", "  AGT-8:\n    params: {check_command: make check}\n")
    assert errors(root) == []
    write_profile(root, "demo", "  AGT-8: true\n")
    assert any("check_command" in e for e in errors(root))


def hook_root(root: Path) -> Path:
    (root / "tools").mkdir()
    shutil.copy(REAL / "tools" / "plan_name_hook.py", root / "tools" / "plan_name_hook.py")
    enforce = ("[{'event': 'afterFileEdit', 'tool': 'tools/plan_name_hook.py', 'args': ['--project', '{project}']},"
               " {'event': 'postToolUse', 'matcher': 'Write', 'tool': 'tools/plan_name_hook.py', 'args': ['--project', '{project}']}]")
    path = root / "rules/shared/agent/AGT-4-plan.md"
    write_rule(root, "rules/shared/agent/AGT-4-plan.md", id="AGT-4", title="План", check="angainor:tools/plan_name_hook.py")
    text = path.read_text(encoding="utf-8").replace("---\n\n#", f"enforce: {enforce}\n---\n\n#", 1)
    path.write_text(text, encoding="utf-8")
    write_profile(root, "demo", "  AGT-4: true\n", repo="demo")
    repos = root / "repos"
    (repos / "demo" / ".cursor").mkdir(parents=True)
    return repos


def test_enforce_projects_hooks_and_keeps_foreign_entries(root):
    repos = hook_root(root)
    hooks = repos / "demo" / ".cursor" / "hooks.json"
    hooks.write_text(json.dumps({"version": 1, "hooks": {"stop": [{"command": "echo foreign"}]}}), encoding="utf-8")
    assert build_rules.main(["--root", str(root), "--projections", "--repos-root", str(repos)]) == 0
    doc = json.loads(hooks.read_text(encoding="utf-8"))
    assert doc["hooks"]["stop"] == [{"command": "echo foreign"}]
    after = doc["hooks"]["afterFileEdit"][0]
    assert after["command"] == "python .cursor/hooks/angainor/plan_name_hook.py --project demo"
    assert doc["hooks"]["postToolUse"][0]["matcher"] == "Write"
    tool = repos / "demo" / ".cursor/hooks/angainor/plan_name_hook.py"
    assert tool.read_text(encoding="utf-8").startswith("# generated by angainor")
    assert build_rules.main(["--root", str(root), "--check", "--repos-root", str(repos)]) == 0


def test_disabled_rule_removes_hooks_and_flags_stale_tool(root, capsys):
    repos = hook_root(root)
    build_rules.main(["--root", str(root), "--projections", "--repos-root", str(repos)])
    write_profile(root, "demo", "  AGT-4:\n    enabled: false\n    reason: тест\n", repo="demo")
    assert build_rules.main(["--root", str(root), "--check", "--repos-root", str(repos)]) == 1
    err = capsys.readouterr().err
    assert "лишний сгенерированный файл" in err and "hooks.json" in err
    build_rules.main(["--root", str(root), "--projections", "--repos-root", str(repos)])
    doc = json.loads((repos / "demo" / ".cursor" / "hooks.json").read_text(encoding="utf-8"))
    assert doc["hooks"] == {}


def test_enforce_tool_must_exist(root):
    hook_root(root)
    (root / "tools" / "plan_name_hook.py").unlink()
    assert any("не найден в angainor" in e for e in errors(root))


def test_matcher_only_for_tool_events(root):
    hook_root(root)
    p = root / "rules/shared/agent/AGT-4-plan.md"
    p.write_text(p.read_text(encoding="utf-8").replace("'event': 'afterFileEdit'", "'event': 'afterFileEdit', 'matcher': 'x'", 1), encoding="utf-8")
    assert any("matcher" in e for e in errors(root))


GITCI_ENFORCE = ("[{'event': 'commit-msg', 'tool': 'scripts/check_commit_msg.py', 'args': ['{arg1}']},"
                 " {'event': 'ci', 'stage': 'commits', 'when': 'pull_request', 'tool': 'scripts/check_commit_msg.py',"
                 " 'args': ['--range', '{pr_range}']}]")


def gitci_root(root: Path, mode: str | None = None) -> Path:
    (root / "scripts").mkdir()
    shutil.copy(REAL / "scripts" / "check_commit_msg.py", root / "scripts" / "check_commit_msg.py")
    path = root / "rules/shared/vcs/CI-8-commits.md"
    write_rule(root, "rules/shared/vcs/CI-8-commits.md", id="CI-8", title="Коммиты", check="angainor:scripts/check_commit_msg.py")
    path.write_text(path.read_text(encoding="utf-8").replace("---\n\n#", f"enforce: {GITCI_ENFORCE}\n---\n\n#", 1), encoding="utf-8")
    write_profile(root, "demo", "  CI-8: true\n", repo="demo")
    if mode:
        prof = root / "rules/projects/demo/project.yaml"
        prof.write_text(prof.read_text(encoding="utf-8") + f"git_hooks: {mode}\n", encoding="utf-8")
    repos = root / "repos"
    (repos / "demo").mkdir(parents=True)
    return repos


def test_githooks_and_ci_projection(root):
    repos = gitci_root(root)
    assert build_rules.main(["--root", str(root), "--projections", "--repos-root", str(repos)]) == 0
    demo = repos / "demo"
    hook = (demo / ".githooks" / "commit-msg").read_text(encoding="utf-8")
    assert hook.startswith("#!/bin/sh") and 'python .angainor/tools/check_commit_msg.py "$1"' in hook
    wf = (demo / ".github/workflows/angainor-commits.yml").read_text(encoding="utf-8")
    assert "origin/${{ github.base_ref }}..HEAD" in wf and "pull_request:" in wf
    assert (demo / ".angainor/tools/check_commit_msg.py").read_text(encoding="utf-8").startswith("# generated by angainor")
    assert build_rules.main(["--root", str(root), "--check", "--repos-root", str(repos)]) == 0


def test_precommit_mode_inserts_replaces_and_removes_block(root):
    repos = gitci_root(root, "pre-commit")
    pc = repos / "demo" / ".pre-commit-config.yaml"
    pc.write_text("repos:\n  - repo: local\n    hooks:\n      - id: mine\n        name: mine\n        entry: echo\n        language: system\n", encoding="utf-8")
    build_rules.main(["--root", str(root), "--projections", "--repos-root", str(repos)])
    text = pc.read_text(encoding="utf-8")
    assert "id: mine" in text and "stages: [commit-msg]" in text and "pass_filenames: true" in text
    assert not (repos / "demo" / ".githooks").exists()
    assert build_rules.main(["--root", str(root), "--check", "--repos-root", str(repos)]) == 0
    write_profile(root, "demo", "  CI-8:\n    enabled: false\n    reason: тест\n", repo="demo")
    prof = root / "rules/projects/demo/project.yaml"
    prof.write_text(prof.read_text(encoding="utf-8") + "git_hooks: pre-commit\n", encoding="utf-8")
    build_rules.main(["--root", str(root), "--projections", "--repos-root", str(repos)])
    assert "angainor" not in pc.read_text(encoding="utf-8") and "id: mine" in pc.read_text(encoding="utf-8")


def test_handwritten_githook_is_not_overwritten(root, capsys):
    repos = gitci_root(root)
    (repos / "demo" / ".githooks").mkdir()
    (repos / "demo" / ".githooks" / "commit-msg").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    assert build_rules.main(["--root", str(root), "--projections", "--repos-root", str(repos)]) == 1
    assert "не сгенерирован" in capsys.readouterr().err


def test_disabled_rule_marks_githook_and_workflow_stale(root, capsys):
    repos = gitci_root(root)
    build_rules.main(["--root", str(root), "--projections", "--repos-root", str(repos)])
    write_profile(root, "demo", "  CI-8:\n    enabled: false\n    reason: тест\n", repo="demo")
    assert build_rules.main(["--root", str(root), "--check", "--repos-root", str(repos)]) == 1
    err = capsys.readouterr().err
    assert "angainor-commits.yml" in err and "commit-msg" in err


def test_ci_requires_stage_and_tool_must_be_stdlib_only(root):
    gitci_root(root)
    p = root / "rules/shared/vcs/CI-8-commits.md"
    p.write_text(p.read_text(encoding="utf-8").replace("'stage': 'commits', ", "", 1), encoding="utf-8")
    assert any("stage" in e for e in errors(root))
    (root / "scripts" / "check_commit_msg.py").write_text("import yaml\n", encoding="utf-8")
    assert any("стандартной библиотеки" in e and "yaml" in e for e in errors(root))


def test_quarantine_requires_manifest_with_all_files(root):
    repos = gitci_root(root)
    q = repos / "demo" / ".cursor" / "_quarantine" / "2026-11-10"
    q.mkdir(parents=True)
    (q / "old-rule.mdc").write_text("x", encoding="utf-8")
    assert any("нет MANIFEST.md" in e for e in check_rules.run(root, repos)[0])
    (q / "MANIFEST.md").write_text("---\ndelete_after: manual\n---\n", encoding="utf-8")
    assert any("old-rule.mdc не описан" in e for e in check_rules.run(root, repos)[0])
    (q / "MANIFEST.md").write_text("---\n---\n| old-rule.mdc | заменено AGT-4 |\n", encoding="utf-8")
    assert any("delete_after" in e for e in check_rules.run(root, repos)[0])
    (q / "MANIFEST.md").write_text("---\ndelete_after: manual\n---\n| old-rule.mdc | заменено AGT-4 |\n", encoding="utf-8")
    assert not any("_quarantine" in e for e in check_rules.run(root, repos)[0])


def test_plan_prefix_from_profile_goes_into_hook_args(root):
    repos = hook_root(root)
    prof = root / "rules/projects/demo/project.yaml"
    prof.write_text(prof.read_text(encoding="utf-8") + "plan_prefix: Demo\n", encoding="utf-8")
    p = root / "rules/shared/agent/AGT-4-plan.md"
    p.write_text(p.read_text(encoding="utf-8").replace("'{project}'", "'{plan_prefix}'"), encoding="utf-8")
    build_rules.main(["--root", str(root), "--projections", "--repos-root", str(repos)])
    doc = json.loads((repos / "demo" / ".cursor" / "hooks.json").read_text(encoding="utf-8"))
    assert doc["hooks"]["afterFileEdit"][0]["command"].endswith("--project Demo")
