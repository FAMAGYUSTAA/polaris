"""
database.py — SQLAlchemy engine, session, and declarative base for the polar station backend.

Uses SQLite as the local data store. Each station runs its own instance of this
backend, so the database file (polar_station.db) lives alongside the application.
SQLite is ideal for the offline-first design: it requires zero server infrastructure
and survives unclean shutdowns common during power-cycling at remote stations.

connect_args={"check_same_thread": False} is required because FastAPI serves
requests across multiple threads, while SQLite's default Python binding restricts
connections to the creating thread.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Resolve the database path relative to this file so it works regardless of cwd.
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(_BASE_DIR, 'polar_station.db')}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency that yields a SQLAlchemy session and guarantees cleanup.

    Usage in a route:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
