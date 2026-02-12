---
description: Workflow for processing Anvisa open data for SNGPC integration
---

# SNGPC Data Processing Workflow

This workflow outlines the steps to ingest, clean, and validate Anvisa's medication data for SNGPC compliance.

## Steps

1. **Download Data**
   - Source: <https://dados.anvisa.gov.br/dados/SNGPC/Industrializados/>
   - Files:
     - `DADOS_ABERTOS_MEDICAMENTOS.csv`
     - `TA_RESTRICAO_MEDICAMENTO.csv`
     - `TA_FABRICANTE_MEDICAMENTO_IFA.CSV`

2. **Data Cleaning**
   - **Load** `DADOS_ABERTOS_MEDICAMENTOS.csv`.
   - **Filter**: Keep only active registrations (`SITUACAO_REGISTRO` == 'VÁLIDO').
   - **Normalize**: Ensure `NU_REGISTRO_PRODUTO` is a 13-digit string (pad with left zeros if necessary).

3. **Enrichment (Join)**
   - **Load** `TA_RESTRICAO_MEDICAMENTO.csv`.
   - **Join**: Left Join with Master Data on `NU_REGISTRO_PRODUTO`.
   - **Flag**: Create an `is_controlled` boolean flag based on `TP_LCV` or restriction text.

4. **Validation**
   - Check for records with "Retenção de Receita" but missing specific List classification.
   - Log warnings for mismatched IFA manufacturers if validating against `TA_FABRICANTE_MEDICAMENTO_IFA`.

5. **Export**
   - Generate a processed dataset (e.g., `processed_sngpc_products.json` or SQL dump) ready for ERP import.
   - Structure should include: `EAN`, `Registro_MS`, `Lista_Controle`, `Tipo_Receituario`.
