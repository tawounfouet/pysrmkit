"""Package import smoke tests."""

import pysrmkit


def test_import_pysrmkit() -> None:
    assert pysrmkit.__version__ == "0.1.0a1"
