from sqlalchemy import create_engine
from config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT

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