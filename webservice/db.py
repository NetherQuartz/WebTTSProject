import os
import datetime as dt

from sqlalchemy import types
from sqlalchemy import Column, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()


class WAVs(Base):
    __tablename__ = "wavs"

    hash = Column(types.String, primary_key=True)
    text = Column(types.String, nullable=False)
    created_at = Column(types.DateTime, nullable=False)
    binary = Column(types.LargeBinary, nullable=False)

    def __init__(self, hash: str, text: str, blob: bytes) -> None:
        super().__init__()

        self.hash = hash
        self.text = text
        self.created_at = dt.datetime.now()
        self.binary = blob


USERNAME = os.getenv("POSTGRES_USER")
PASSWORD = os.getenv("POSTGRES_PASSWORD")
DATABASE = os.getenv("POSTGRES_DB")

DB_HOST = "tts-postgres"
DB_PORT = 5432

ENGINE = create_engine(f"postgresql://{USERNAME}:{PASSWORD}@{DB_HOST}:{DB_PORT}/{DATABASE}")

Base.metadata.create_all(ENGINE)

SESSION_MAKER = sessionmaker(bind=ENGINE)
