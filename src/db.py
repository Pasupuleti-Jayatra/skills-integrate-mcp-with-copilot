from pathlib import Path
from sqlmodel import create_engine, SQLModel, Session

DB_FILE = Path(__file__).resolve().parent.parent / "data.db"
DATABASE_URL = f"sqlite:///{DB_FILE}"

# For SQLite, allow check_same_thread False for multithreaded servers
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})


def init_db() -> None:
    """Create database and tables."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Yield a session for dependency injection."""
    with Session(engine) as session:
        yield session
