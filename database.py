from sqlmodel import SQLModel, create_engine, Session
from config import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.APP_ENV == "development",
    connect_args={"check_same_thread": False},  # สำหรับ SQLite เท่านั้น
)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency สำหรับ inject DB session เข้า endpoint"""
    with Session(engine) as session:
        yield session