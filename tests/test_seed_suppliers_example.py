"""Qualification for the idempotent Supplier integration seed."""

from examples.seed_suppliers import SUPPLIERS, seed_suppliers

from pysrmkit import PySRMKit


def test_supplier_seed_is_idempotent() -> None:
    srm = PySRMKit.in_memory()

    first_created, first_skipped = seed_suppliers(srm)
    second_created, second_skipped = seed_suppliers(srm)

    assert (first_created, first_skipped) == (len(SUPPLIERS), 0)
    assert (second_created, second_skipped) == (0, len(SUPPLIERS))
    assert srm.suppliers.list().total == len(SUPPLIERS)
