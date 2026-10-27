"""SQLAlchemy Session factory for persistence adapters."""

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create Sessions bound to an externally owned Engine."""

    return sessionmaker(bind=engine)
