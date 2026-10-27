"""SQLAlchemy Session factory foundation tests."""

from sqlalchemy import select

from pysrmkit.adapters.sqlalchemy.engine import create_persistence_engine
from pysrmkit.adapters.sqlalchemy.session import create_session_factory


def test_session_factory_uses_externally_created_engine() -> None:
    engine = create_persistence_engine("sqlite:///:memory:")
    session_factory = create_session_factory(engine)

    try:
        with session_factory() as session:
            assert session.get_bind() is engine
            assert session.scalar(select(1)) == 1
    finally:
        engine.dispose()
