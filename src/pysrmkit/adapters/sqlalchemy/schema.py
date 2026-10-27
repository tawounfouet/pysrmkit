"""Persistence schema registration helpers."""

from importlib import import_module

from sqlalchemy import MetaData

from pysrmkit.adapters.sqlalchemy.metadata import PersistenceBase


def load_persistence_metadata() -> MetaData:
    """Load every persistence record and return the populated adapter metadata."""

    import_module("pysrmkit.adapters.sqlalchemy.models")
    return PersistenceBase.metadata
