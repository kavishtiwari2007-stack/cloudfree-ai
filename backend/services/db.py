from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

# Create engine with connection pool parameters
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600
)

# Session maker for transaction contexts
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db():
    """Dependency generator injecting thread-safe database session contexts"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_postgis_support() -> bool:
    """Verifies that the database has PostGIS extensions active"""
    db = SessionLocal()
    try:
        # Run query checking postgis version
        result = db.execute(text("SELECT postgis_full_version();"))
        version = result.scalar()
        print(f"PostGIS Connection Validated: {version}")
        return True
    except Exception as e:
        print(f"PostGIS verification failed (Is extension installed?): {e}")
        return False
    finally:
        db.close()
