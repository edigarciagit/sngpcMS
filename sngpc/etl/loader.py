from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
import logging
from ..api.database import Base
from ..api.models import Product

logger = logging.getLogger(__name__)

def load_to_db(df: pd.DataFrame, db_url: str):
    """
    Loads processed dataframe into SQLite database.
    """
    logger.info(f"Connecting to database: {db_url}")
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        logger.info(f"Loading {len(df)} records to database...")
        
        # Rename columns to match DB schema if necessary or map them
        # For bulk insert, to_sql is faster than ORM for large datasets
        records = df[['NUMERO_REGISTRO_PRODUTO', 'NOME_PRODUTO', 'is_controlled', 'ST_RESTRITO_HOSPITAL']].copy()
        records.columns = ['numero_registro', 'nome_produto', 'is_controlled', 'restriction_detail']
        
        # Use pandas to_sql for performance
        records.to_sql('products', engine, if_exists='replace', index=False, chunksize=1000)
        
        logger.info("Database load complete.")
        
    except Exception as e:
        logger.error(f"Failed to load database: {e}")
        raise
    finally:
        session.close()
