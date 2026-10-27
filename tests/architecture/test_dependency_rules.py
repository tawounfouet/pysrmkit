"""Executable dependency rules for the PySRMKit package boundaries."""

from __future__ import annotations

import ast
from pathlib import Path

PACKAGE_ROOT = Path(__file__).parents[2] / "src" / "pysrmkit"

FORBIDDEN_IMPORTS: dict[str, tuple[str, ...]] = {
    "domain": (
        "pysrmkit.application",
        "pysrmkit.ports",
        "pysrmkit.adapters",
        "pysrmkit.public",
    ),
    "application": ("pysrmkit.adapters", "pysrmkit.public"),
    "ports": ("pysrmkit.adapters", "pysrmkit.public"),
}

FORBIDDEN_INFRASTRUCTURE_IMPORTS = (
    "sqlalchemy",
    "alembic",
    "psycopg",
)


def _imported_modules(tree: ast.AST) -> list[str]:
    modules: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            modules.append(node.module)

    return modules


def _is_forbidden(module: str, forbidden_prefixes: tuple[str, ...]) -> bool:
    return any(module == prefix or module.startswith(f"{prefix}.") for prefix in forbidden_prefixes)


def test_package_dependency_rules() -> None:
    for layer, forbidden_prefixes in FORBIDDEN_IMPORTS.items():
        layer_root = PACKAGE_ROOT / layer

        for python_file in layer_root.rglob("*.py"):
            tree = ast.parse(python_file.read_text(encoding="utf-8"))

            for module in _imported_modules(tree):
                assert not _is_forbidden(module, forbidden_prefixes), (
                    f"{python_file.relative_to(PACKAGE_ROOT)} imports forbidden "
                    f"dependency {module!r}"
                )


def test_core_layers_do_not_import_persistence_frameworks() -> None:
    for layer in ("domain", "application", "ports"):
        layer_root = PACKAGE_ROOT / layer

        for python_file in layer_root.rglob("*.py"):
            tree = ast.parse(python_file.read_text(encoding="utf-8"))

            for module in _imported_modules(tree):
                assert not _is_forbidden(module, FORBIDDEN_INFRASTRUCTURE_IMPORTS), (
                    f"{python_file.relative_to(PACKAGE_ROOT)} imports persistence "
                    f"infrastructure {module!r}"
                )
