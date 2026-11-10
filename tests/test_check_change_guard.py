"""Тесты tools/check_change_guard.py (AGT-9) и tools/check_pr_size.py (AGT-10)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import check_change_guard as guard  # noqa: E402
import check_pr_size as size  # noqa: E402


class Repo:
    def __init__(self, path: Path):
        self.path = path
        self.git("init", "-q")
        self.write("app.py", "x = 1\n")
        self.write("tests/test_app.py", "def test_a():\n    assert True\n\n\ndef test_b():\n    assert True\n")
        self.write("pyproject.toml", "[tool.coverage.report]\nfail_under = 80\n")
        self.commit("chore: init")

    def git(self, *a):
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=self.path, check=True, capture_output=True)

    def write(self, rel: str, text: str):
        p = self.path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    def commit(self, msg: str):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", msg)


@pytest.fixture()
def repo(tmp_path, monkeypatch):
    r = Repo(tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GITHUB_STEP_SUMMARY", raising=False)
    return r


def run(argv=None):
    return guard.main(["--range", "HEAD~1..HEAD"] if argv is None else argv)


def test_clean_change_passes(repo):
    repo.write("app.py", "x = 2\n")
    repo.commit("fix: поправить")
    assert run() == 0


def test_noqa_blocks_until_trailer(repo, capsys):
    repo.write("app.py", "import os  # noqa\n")
    repo.commit("fix: поправить")
    assert run() == 1
    assert "noqa" in capsys.readouterr().err
    repo.write("app.py", "import os  # noqa\nx = 3\n")
    repo.commit("fix: ещё\n\nChecks-Change: библиотека требует неиспользуемый импорт")
    assert guard.main(["--range", "HEAD~2..HEAD"]) == 0


def test_skip_and_workflow_and_deleted_test(repo):
    repo.write("tests/test_app.py", "import pytest\n\n\n@pytest.mark.skip\ndef test_a():\n    assert True\n")
    repo.write(".github/workflows/ci.yml", "name: ci\n")
    repo.commit("fix: позеленить")
    findings = guard.analyze(guard.read_diff("HEAD~1..HEAD"))
    joined = "\n".join(findings)
    assert "skip/xfail" in joined and "удалено тестов — 1" in joined and "ci.yml" in joined
    assert run() == 1


def test_threshold_lowered_blocks_raised_passes(repo):
    repo.write("pyproject.toml", "[tool.coverage.report]\nfail_under = 70\n")
    repo.commit("chore: порог")
    assert run() == 1
    repo.write("pyproject.toml", "[tool.coverage.report]\nfail_under = 90\n")
    repo.commit("chore: порог выше")
    findings = guard.analyze(guard.read_diff("HEAD~1..HEAD"))
    assert not any("ослаблен" in f for f in findings)


def test_pyproject_without_check_settings_is_not_flagged(repo):
    repo.write("pyproject.toml", "[tool.coverage.report]\nfail_under = 80\n\n[project]\nname = 'x'\n")
    repo.commit("chore: имя")
    assert not any("pyproject" in f for f in guard.analyze(guard.read_diff("HEAD~1..HEAD")))


def test_summary_written(repo, tmp_path, monkeypatch):
    out = tmp_path / "summary.md"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(out))
    repo.write("app.py", "x = 1  # type: ignore\n")
    repo.commit("fix: x\n\nChecks-Change: нужен для старого API")
    assert run() == 0
    text = out.read_text(encoding="utf-8")
    assert "type: ignore" in text and "нужен для старого API" in text


def test_pr_size(repo):
    repo.write("big.txt", "\n".join(f"line {i}" for i in range(30)))
    repo.write("uv.lock", "\n".join("x" for _ in range(500)))
    repo.commit("feat: много")
    assert size.main(["--range", "HEAD~1..HEAD", "--max-lines", "40"]) == 0
    assert size.measure("HEAD~1..HEAD") == (30, 1)
    assert size.main(["--range", "HEAD~1..HEAD", "--max-lines", "10"]) == 1
    repo.write("big.txt", "\n".join(f"line {i}" for i in range(31)))
    repo.commit("feat: ещё\n\nLarge-Change: генерируемая таблица")
    assert size.main(["--range", "HEAD~2..HEAD", "--max-lines", "10"]) == 0
