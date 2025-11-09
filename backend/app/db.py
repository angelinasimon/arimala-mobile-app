from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Load environment variables from .env (for local dev)
from dotenv import load_dotenv
load_dotenv()  # this will load variables from a .env file into os.environ

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./arimala_dev.db")
# Default to a SQLite file 'arimala_dev.db' in the backend directory if DATABASE_URL not set

# Create SQLAlchemy engine and session factory
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
