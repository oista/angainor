"""Тесты tools/plan_name_hook.py (AGT-4)."""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import plan_name_hook as hook  # noqa: E402


def make_plan(root: Path, filename: str, name: str) -> Path:
    d = root / ".cursor" / "plans"
    d.mkdir(parents=True, exist_ok=True)
    p = d / filename
    p.write_text(f"---\nname: {name}\noverview: x\n---\n# План\n", encoding="utf-8")
    return p


def run(monkeypatch, capsys, payload: dict, project="clavis") -> str:
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))
    assert hook.main(["--project", project]) == 0
    return capsys.readouterr().out.strip()


def test_adds_prefix_and_renames(tmp_path, monkeypatch, capsys):
    p = make_plan(tmp_path, "hardening_ab12cd34.plan.md", "Control Hub hardening")
    out = run(monkeypatch, capsys, {"file_path": str(p)})
    assert out == "{}"
    new = tmp_path / ".cursor" / "plans" / "clavis_control_hub_hardening_ab12cd34.plan.md"
    assert new.exists() and not p.exists()
    assert "name: clavis: Control Hub hardening" in new.read_text(encoding="utf-8")


def test_already_normalized_is_untouched(tmp_path, monkeypatch, capsys):
    p = make_plan(tmp_path, "clavis_topic.plan.md", "clavis: Topic")
    before = p.read_text(encoding="utf-8")
    run(monkeypatch, capsys, {"tool_input": {"path": str(p)}})
    assert p.exists() and p.read_text(encoding="utf-8") == before


def test_relative_path_uses_workspace_root(tmp_path, monkeypatch, capsys):
    make_plan(tmp_path, "topic.plan.md", "Topic")
    run(monkeypatch, capsys, {"file_path": ".cursor/plans/topic.plan.md", "workspace_roots": [str(tmp_path)]})
    assert (tmp_path / ".cursor" / "plans" / "clavis_topic.plan.md").exists()


def test_ignores_other_files_and_garbage(tmp_path, monkeypatch, capsys):
    other = tmp_path / "docs" / "x.plan.md"
    other.parent.mkdir()
    other.write_text("name: X\n", encoding="utf-8")
    assert run(monkeypatch, capsys, {"file_path": str(other)}) == "{}"
    assert other.read_text(encoding="utf-8") == "name: X\n"
    monkeypatch.setattr(sys, "stdin", io.StringIO("не json"))
    assert hook.main(["--project", "clavis"]) == 0
    assert capsys.readouterr().out.strip() == "{}"
