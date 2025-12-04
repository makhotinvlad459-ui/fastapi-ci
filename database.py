from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

SQLAlchemy_DB = "sqlite:///./cook.db"

engine = create_engine(
    SQLAlchemy_DB, connect_args={"check_same_thread": False}, echo=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
