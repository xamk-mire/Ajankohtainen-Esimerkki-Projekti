from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base; later models register tables on ``Base.metadata``."""
