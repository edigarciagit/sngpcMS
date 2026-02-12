import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import pandas as pd
from sngpc.etl.parser import load_medications, enrich_data

class TestSNGPCPipeline(unittest.TestCase):
    
    def test_load_medications_cleaning(self):
        # Mock CSV data
        mock_csv = Path("mock_meds.csv")
        with open(mock_csv, "w") as f:
            f.write("NUMERO_REGISTRO_PRODUTO;NOME_PRODUTO;SITUACAO_REGISTRO\n")
            f.write("1.2345.6789.001-1;Med A;VÁLIDO\n")
            f.write("987654321;Med B;VÁLIDO\n")
            f.write("123;Med C;CANCELADO\n")
            
        try:
            df = load_medications(mock_csv)
            
            # Check filtering
            self.assertEqual(len(df), 2)
            
            # Check normalization
            self.assertEqual(df.iloc[0]['NUMERO_REGISTRO_PRODUTO'], "1234567890011")
            
        finally:
            mock_csv.unlink()

    def test_enrich_data(self):
        meds = pd.DataFrame({
            'NOME_PRODUTO': ['Paracetamol', 'Med B'],
            'NOME_PRODUTO_NORM': ['PARACETAMOL', 'MED B']
        })
        restr = pd.DataFrame({
            'NO_PRODUTO': ['Med B'],
            'NO_PRODUTO_NORM': ['MED B'],
            'DS_RESTRICAO_PRESCRICAO': ['VENDA SOB PRESCRICAO MEDICA']
        })
        
        result = enrich_data(meds, restr)
        
        self.assertTrue(result.loc[result['NOME_PRODUTO'] == 'Med B', 'is_controlled'].values[0])
        self.assertFalse(result.loc[result['NOME_PRODUTO'] == 'Paracetamol', 'is_controlled'].values[0])

    def test_enrich_data_fuzzy(self):
        meds = pd.DataFrame({
            'NOME_PRODUTO': ['ASPIRINA 100MG'],
            'NOME_PRODUTO_NORM': ['ASPIRINA 100MG']
        })
        # Typo in restriction data
        restr = pd.DataFrame({
            'NO_PRODUTO': ['ASPIRINA 100 MG'], # Extra space
            'NO_PRODUTO_NORM': ['ASPIRINA 100 MG'],
            'DS_RESTRICAO_PRESCRICAO': ['VENDA SOB PRESCRICAO MEDICA']
        })
        
        result = enrich_data(meds, restr)
        
        # Should match despite the small difference
        self.assertTrue(result.loc[0, 'is_controlled'])
        self.assertEqual(result.loc[0, 'FUZZY_MATCH_NAME'], 'ASPIRINA 100 MG')

if __name__ == '__main__':
    unittest.main()
