import logging
from pathlib import Path
import yaml
import pandas as pd
from .downloader import download_file
from .parser import load_medications, load_restrictions, enrich_data
from .loader import load_to_db

# Simple config loader
def load_config():
    with open('config/config.yaml', 'r') as f:
        return yaml.safe_load(f)

def run_pipeline():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("SNGPC-Pipeline")
    
    config = load_config()
    raw_dir = Path(config['paths']['raw_data'])
    processed_dir = Path(config['paths']['processed_data'])
    base_url = config['anvisa']['base_url']
    db_url = config.get('database', {}).get('url', 'sqlite:///data/sngpc.db')
    
    # 1. Download
    meds_file = download_file(base_url + "DADOS_ABERTOS_MEDICAMENTOS.csv", raw_dir / "medications.csv")
    restr_file = download_file(base_url + "TA_RESTRICAO_MEDICAMENTO.csv", raw_dir / "restrictions.csv")
    
    # 2. Parse
    df_meds = load_medications(meds_file)
    df_restr = load_restrictions(restr_file)
    
    # 3. Transform
    df_final = enrich_data(df_meds, df_restr)
    
    # 4. Save (JSON)
    output_path = processed_dir / "sngpc_products.json"
    logger.info(f"Saving {len(df_final)} records to {output_path}...")
    df_final.to_json(output_path, orient='records', indent=2)

    # 5. Load (Database)
    load_to_db(df_final, db_url)
    
    logger.info("Pipeline finished successfully.")

if __name__ == "__main__":
    run_pipeline()
