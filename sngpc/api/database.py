from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import yaml
from pathlib import Path

def load_config():
    config_path = Path("config/config.yaml")
    if config_path.exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {}

config = load_config()
SQLALCHEMY_DATABASE_URL = config.get('database', {}).get('url', "sqlite:///./data/sngpc.db")

# check_same_thread needed for SQLite
connect_args = {"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args=connect_args
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
