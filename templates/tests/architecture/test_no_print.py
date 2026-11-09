# canon: TST-4, LOG-1, LAY-3
"""Архитектурный тест: в коде пакета нет print, кроме точек входа CLI."""

from __future__ import annotations

import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "src"
ENTRY_POINTS = {"__main__.py", "cli.py", "settings.py"}


def _print_calls(path: Path) -> list[int]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "print"
    ]


def test_no_print_outside_entry_points() -> None:
    offenders = [
        f"{path.relative_to(SRC)}:{line}"
        for path in SRC.rglob("*.py")
        if path.name not in ENTRY_POINTS
        for line in _print_calls(path)
    ]
    assert not offenders, "print вне точек входа CLI (используйте logger): " + ", ".join(offenders)
