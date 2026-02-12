import pandas as pd
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def load_medications(path: Path) -> pd.DataFrame:
    """
    Loads and cleans medication data.
    """
    logger.info(f"Loading medications from {path}...")
    # Read with appropriate columns
    df = pd.read_csv(path, sep=';', encoding='latin1', dtype={'NUMERO_REGISTRO_PRODUTO': str})
    
    # Filter active registrations
    if 'SITUACAO_REGISTRO' in df.columns:
        df = df[df['SITUACAO_REGISTRO'].astype(str).str.contains('VÁLIDO', case=False, na=False)]
    
    # Normalize registration number
    df['NUMERO_REGISTRO_PRODUTO'] = df['NUMERO_REGISTRO_PRODUTO'].astype(str).str.replace(r'\D', '', regex=True)
    
    # Normalize name for merging
    df['NOME_PRODUTO_NORM'] = df['NOME_PRODUTO'].astype(str).str.upper().str.strip()
    
    return df

def load_restrictions(path: Path) -> pd.DataFrame:
    """
    Loads restriction data.
    """
    logger.info(f"Loading restrictions from {path}...")
    try:
        df = pd.read_csv(path, sep=';', encoding='latin1', on_bad_lines='warn')
    except Exception as e:
        logger.error(f"Failed to load restrictions: {e}")
        # Return empty DF ensuring columns exist to avoid downstream errors
        return pd.DataFrame(columns=['NO_PRODUTO', 'NO_PRODUTO_NORM', 'DS_RESTRICAO_PRESCRICAO'])
    
    # Normalize name for merging
    df['NO_PRODUTO_NORM'] = df['NO_PRODUTO'].astype(str).str.upper().str.strip()
    
    return df

from rapidfuzz import process, fuzz

def enrich_data(meds: pd.DataFrame, restr: pd.DataFrame) -> pd.DataFrame:
    """
    Joins medications with restrictions using exact match + fuzzy match fallback.
    """
    logger.info("Joining medications and restrictions (Exact + Fuzzy)...")
    
    # 1. Exact Match
    merged = pd.merge(meds, restr, left_on='NOME_PRODUTO_NORM', right_on='NO_PRODUTO_NORM', how='left')
    
    # 2. Identify unmatched records
    unmatched_mask = merged['NO_PRODUTO_NORM'].isna()
    unmatched_meds = meds[unmatched_mask].copy()
    
    if not unmatched_meds.empty and not restr.empty:
        logger.info(f"Attempting fuzzy match for {len(unmatched_meds)} records...")
        
        # Create a list of unique names for matching
        choices = restr['NO_PRODUTO_NORM'].dropna().unique().tolist()
        
        def find_best_match(name):
            if not isinstance(name, str): return None
            match = process.extractOne(name, choices, scorer=fuzz.token_sort_ratio)
            if match:
                logger.debug(f"Fuzzy match for '{name}': {match[0]} (Score: {match[1]})")
                if match[1] >= 80:  # Lowered threshold to 80%
                    return match[0]
            return None

        # Apply fuzzy matching (this can be slow on large datasets)
        # Optimizing: Only apply to unique names to reduce calls
        unique_unmatched = unmatched_meds['NOME_PRODUTO_NORM'].unique()
        fuzzy_matches = {name: find_best_match(name) for name in unique_unmatched}
        
        # Map back to dataframe
        unmatched_meds['FUZZY_MATCH_NAME'] = unmatched_meds['NOME_PRODUTO_NORM'].map(fuzzy_matches)
        
        # Merge again using the fuzzy match name
        fuzzy_merged = pd.merge(unmatched_meds, restr, left_on='FUZZY_MATCH_NAME', right_on='NO_PRODUTO_NORM', how='left')
        
        # Update original merged dataframe
        # We drop the rows that were unmatched and append the fuzzy matched ones
        merged = merged[~unmatched_mask]
        merged = pd.concat([merged, fuzzy_merged], ignore_index=True)
    
    # Create is_controlled flag
    merged['is_controlled'] = merged['DS_RESTRICAO_PRESCRICAO'].astype(str).str.contains('VENDA SOB PRESCRICAO MEDICA', case=False, na=False)
                              
    return merged
