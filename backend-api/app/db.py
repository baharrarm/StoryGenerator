from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from sqlalchemy.exc import OperationalError
import os
from app.config import DATABASE_URL

DB_SSLMODE = os.getenv("DB_SSLMODE", "disable")          # was: "require" (AWS RDS)
DB_SCHEMA  = os.getenv("DB_SCHEMA",  "public")           # was: "s021"   (AWS RDS schema)

engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={
        # "sslmode": "require",                           # AWS RDS required SSL
        "sslmode": DB_SSLMODE,
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
        # "options": "-c search_path=s021,public",        # AWS RDS schema
        "options": f"-c search_path={DB_SCHEMA},public",
    },
    future=True,
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        try:
            db.close()
        except OperationalError:
            pass  # ignore if RDS killed the conn
