from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import DATABASE_URL, IS_EXTERNAL_DB

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,       # replace connections older than 5 min (before Render idle-closes them)
    pool_size=5,
    max_overflow=2,
    connect_args={"sslmode": "require"} if IS_EXTERNAL_DB else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)