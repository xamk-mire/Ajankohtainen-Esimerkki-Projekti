"""Seed the system catalog. From backend/: python -m app.db.init_db"""

from app.db.session import SessionLocal
from app.services.seed import seed_catalog


def init_db() -> None:
    db = SessionLocal()
    try:
        seed_catalog(db)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
