"""Reset and seed demonstration data. From backend/: python -m app.db.init_db"""

from app.db.session import SessionLocal
from app.services.seed import DEMO_EMAIL, DEMO_PASSWORD, reset_and_seed


def init_db() -> None:
    db = SessionLocal()
    try:
        reset_and_seed(db)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
    print(f"Demo login: {DEMO_EMAIL}")
    print(f"Password: {DEMO_PASSWORD}")


if __name__ == "__main__":
    init_db()
