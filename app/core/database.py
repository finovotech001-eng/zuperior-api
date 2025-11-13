from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from .config import settings


def clean_database_url(url: str) -> str:
    """
    Remove invalid connection parameters from DATABASE_URL.
    PostgreSQL connection strings don't support 'schema' as a connection parameter.
    """
    try:
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        
        # Remove invalid parameters
        invalid_params = ['schema']  # Add other invalid params if needed
        for param in invalid_params:
            query_params.pop(param, None)
        
        # Reconstruct URL without invalid parameters
        new_query = urlencode(query_params, doseq=True)
        new_parsed = parsed._replace(query=new_query)
        cleaned_url = urlunparse(new_parsed)
        
        return cleaned_url
    except Exception:
        # If parsing fails, return original URL
        return url


# Clean the DATABASE_URL to remove invalid parameters
database_url = clean_database_url(settings.DATABASE_URL)

engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Dependency to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



