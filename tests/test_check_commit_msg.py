"""Тесты scripts/check_commit_msg.py (CI-8)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_commit_msg as ccm  # noqa: E402


@pytest.mark.parametrize("msg", [
    "feat: добавить реестр",
    "fix(rules): поправить схему",
    "feat(api)!: сломать контракт",
    "docs: ADR-0003\n\nтело\n\nCo-Authored-By: X",
    'Revert "feat: x"',
    "Merge branch 'main' into feat/x",
    "fixup! feat: x",
    "# комментарий git\nchore: обновить зависимости",
])
def test_valid(msg):
    assert ccm.check_message(msg) == []


@pytest.mark.parametrize("msg", [
    "Добавил реестр",
    "feat:без пробела",
    "feature: x",
    "feat(): x",
    "feat: ",
    "",
])
def test_invalid(msg):
    assert ccm.check_message(msg)


def test_header_too_long():
    assert any("100" in e for e in ccm.check_message("feat: " + "я" * 100))


def test_file_mode(tmp_path):
    f = tmp_path / "MSG"
    f.write_text("плохое сообщение", encoding="utf-8")
    assert ccm.main([str(f)]) == 1
    f.write_text("fix: ok", encoding="utf-8")
    assert ccm.main([str(f)]) == 0


def test_range_mode(tmp_path, monkeypatch):
    def git(*a):
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a],
                       cwd=tmp_path, check=True, capture_output=True)

    git("init", "-q")
    (tmp_path / "a").write_text("1")
    git("add", "a")
    git("commit", "-q", "-m", "chore: init")
    (tmp_path / "a").write_text("2")
    git("commit", "-q", "-am", "плохо")
    monkeypatch.chdir(tmp_path)
    assert ccm.main(["--range", "HEAD~1..HEAD"]) == 1
    (tmp_path / "a").write_text("3")
    git("commit", "-q", "-am", "fix: ok")
    assert ccm.main(["--range", "HEAD~1..HEAD"]) == 0


def test_requires_mode():
    with pytest.raises(SystemExit):
        ccm.main([])
