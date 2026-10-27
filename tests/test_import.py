"""Package import smoke tests."""

import importlib

import pysrmkit

BOOTSTRAP_MODULES = (
    "pysrmkit",
    "pysrmkit.domain",
    "pysrmkit.application",
    "pysrmkit.ports",
    "pysrmkit.adapters",
)


def test_bootstrap_packages_import() -> None:
    for module_name in BOOTSTRAP_MODULES:
        module = importlib.import_module(module_name)
        assert module.__name__ == module_name


def test_package_version() -> None:
    assert pysrmkit.__version__ == "0.1.0a3"
