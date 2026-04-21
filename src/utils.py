"""
Helper functions used by other modules
"""
from datetime import datetime, timezone
from sqlalchemy import create_engine
from config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT, LOG_PATH

def log(message, level="INFO", echo=False):
    """
    Write a timestamped message to the log file and optionally print it.
    """

    timestamp = datetime.now(timezone.utc)

    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(f'{timestamp} UTC: [{level}] {message}\n')

    if echo is True:
        print(f'{timestamp} UTC: [{level}] {message}\n')

def connect_to_database():
    """
    Creates and returns SQLAlchemy engine for database connection
    """
    connection_string = (
        f"postgresql://{DB_USER}:{DB_PASSWORD or ''}@"
        f"{DB_HOST}:{DB_PORT or '5432'}/{DB_NAME}"
    )
    engine = create_engine(connection_string)
    return engine

def to_int(value):
    return int(value) if value not in (None, '') else None