from src.db import init_db
from src.app import seed_db_if_empty
from src.db import engine
from sqlmodel import Session, select
from src.models import Activity


def test_seed_and_query():
    # Ensure fresh DB schema
    init_db()
    with Session(engine) as session:
        # seed
        seed_db_if_empty(session)
        statement = select(Activity)
        activities = session.exec(statement).all()
        assert len(activities) >= 1
