from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Define the path to the SQLite database
DATABASE_URL = "sqlite:///./tasks.db"

# Create the SQLAlchemy engine for interacting with the database
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Required only for SQLite
)

# This will be used to create database sessions in our app
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

# Base class that all ORM models will inherit from
Base = declarative_base()
