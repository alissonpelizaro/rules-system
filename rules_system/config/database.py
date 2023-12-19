import os
import sqlalchemy

from sqlalchemy.orm import sessionmaker, declarative_base

def get_database_url() -> str:
    """get_database_url returns the database url from the environment variable
    DATABASE_URL or a local Sqlite URL.

    Returns:
        str: The database url
    """
    return os.getenv(
        'DATABASE_URL',
        'sqlite:///:memory:' if os.getenv(
            'PYTEST_CURRENT_TEST'
        ) else 'postgresql+pg8000://dbuser:dbpass@localhost/rulessystem'
    )
    
engine = sqlalchemy.create_engine(get_database_url())

Session = sessionmaker(autocommit=False,
                       expire_on_commit=False,
                       autoflush=False,
                       bind=engine)

Base = declarative_base()
